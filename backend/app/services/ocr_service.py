"""
OCR Service — Stage 1 of the extraction pipeline.

Responsibility: convert the uploaded file into raw text transcriptions,
one per page. Nothing more. Parsing, validation, and analysis are handled
downstream by the LabContemplator (Stage 2).
"""

import asyncio
import logging
from pathlib import Path
from pdf2image import convert_from_path
from app.services.ollama_client import llm
from app.services.lab_contemplator import lab_contemplator
from app.models.lab_report import LabValue, HealthAnalysis
from app.config import settings

logger = logging.getLogger(__name__)

# Vision model prompt — ask ONLY for raw transcription.
# Qwen2-VL and similar models perform much better when not forced to produce JSON.
# Structured extraction is handled by the contemplation model in Stage 2.
VISION_TRANSCRIBE_PROMPT = """You are reading a medical laboratory report.

Your ONLY job is to transcribe every piece of text and every number you can see.

For each lab test result, write it on its own line like this:
  Test Name | Value | Unit | Reference Range

Also transcribe:
- Patient name/ID if visible
- Date of the report
- Lab name / hospital name
- Any doctor notes or comments
- Any test that has a value, even if you're unsure of the name

Do NOT summarise. Do NOT interpret. Do NOT skip anything.
Transcribe EXACTLY what you see, line by line."""


class OCRService:
    async def process_report(
        self,
        file_path: str,
        preferences: dict,
    ) -> tuple[dict, HealthAnalysis]:
        """
        Full pipeline:
          Stage 1 (here)  — vision model transcribes each page to raw text
          Stage 2 (contemplator) — validates, structures, analyses the raw text
        """
        image_paths = await self._prepare_images(file_path)

        raw_pages: list[str] = []
        for img_path in image_paths:
            logger.info("[OCR] Stage 1 — transcribing: %s", img_path)
            text = await self._transcribe_image(img_path)
            if text.strip():
                logger.info("[OCR] Page transcription (%d chars):\n%s", len(text), text[:400])
                raw_pages.append(text)
            else:
                logger.warning("[OCR] Vision model returned empty output for %s", img_path)

        if not raw_pages:
            logger.error("[OCR] Vision model produced no output for any page")
            return {}, HealthAnalysis(
                issues=["Vision model could not read this document"],
                risk_factors=[],
                recommendations=["Try a clearer scan or a different file format"],
            )

        logger.info("[OCR] Stage 1 complete — %d page(s) transcribed. Passing to contemplator...", len(raw_pages))

        # Stage 2 — hand off ALL pages to the contemplation model
        lab_data, health_analysis = await lab_contemplator.process(raw_pages, preferences)
        return lab_data, health_analysis

    async def _prepare_images(self, file_path: str) -> list[str]:
        """
        PDFs → convert to PNG pages at 200 DPI, saved under uploads/images/<stem>/
        Images → return as-is
        """
        path = Path(file_path)

        if path.suffix.lower() == ".pdf":
            # uploads/pdfs/<stem>.pdf → uploads/images/<stem>/page0.png ...
            images_dir = path.parent.parent / "images" / path.stem
            images_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[OCR] Converting PDF → PNG (200 DPI) into %s", images_dir)

            # Run synchronous pdf2image in a thread so the event loop is not blocked
            pages = await asyncio.to_thread(convert_from_path, str(path), dpi=200)
            img_paths = []
            for i, page in enumerate(pages):
                img_path = images_dir / f"page{i}.png"
                page.save(str(img_path), "PNG")
                img_paths.append(str(img_path))

            logger.info("[OCR] %d page(s) converted", len(img_paths))
            return img_paths

        return [str(path)]

    async def _transcribe_image(self, image_path: str) -> str:
        """Stage 1 — call vision model to transcribe a single page image, with retries."""
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = await llm.generate_with_image(
                    model=settings.vision_model,
                    prompt=VISION_TRANSCRIBE_PROMPT,
                    image_path=image_path,
                )
                return response.strip()
            except Exception as e:
                last_error = e
                if attempt < 3:
                    wait = 2 ** (attempt - 1)  # 1s, 2s
                    logger.warning(
                        "[OCR] Vision model failed (attempt %d/3) on %s: %s — retrying in %ds",
                        attempt, image_path, e, wait,
                    )
                    await asyncio.sleep(wait)

        logger.error("[OCR] Vision model failed after 3 attempts on %s: %s", image_path, last_error)
        return ""


ocr_service = OCRService()
