import httpx
import base64
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.base_url = settings.ollama_url
        self.timeout = httpx.Timeout(float(settings.ollama_timeout))

    async def _post(self, messages: list[dict], model: str, max_tokens: int) -> str:
        """Core method — all calls route through here."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug("POST %s/v1/chat/completions model=%s max_tokens=%d", self.base_url, model, max_tokens)
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={"model": model, "messages": messages, "max_tokens": max_tokens},
            )
            if response.status_code != 200:
                # Do NOT log response body — it may contain patient data from the prompt
                logger.error("LM Studio HTTP %d on model=%s", response.status_code, model)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            logger.debug("Response from %s (%d chars)", model, len(content))
            return content

    async def generate(self, model: str, prompt: str, num_predict: int = 8192) -> str:
        """Single-turn text generation."""
        return await self._post(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=num_predict,
        )

    async def generate_with_image(self, model: str, prompt: str, image_path: str) -> str:
        """Vision model — auto-detects PNG vs JPEG MIME type.

        8192 tokens is the safe ceiling for a dense multi-page lab report
        transcription. 2048 was truncating output mid-page.
        """
        ext = image_path.lower()
        if ext.endswith(".png"):
            mime = "image/png"
        elif ext.endswith(".jpg") or ext.endswith(".jpeg"):
            mime = "image/jpeg"
        else:
            mime = "image/png"  # safe default for converted PDFs

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
                ],
            }
        ]
        return await self._post(messages=messages, model=model, max_tokens=8192)

    async def chat(self, model: str, messages: list[dict]) -> str:
        """Multi-turn chat."""
        return await self._post(messages=messages, model=model, max_tokens=8192)


llm = LLMClient()
