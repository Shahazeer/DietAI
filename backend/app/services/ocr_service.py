import json
import re
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from app.services.ollama_client import ollama
from app.models.lab_report import LabValue, HealthAnalysis
from app.config import settings

EXTRACTION_PROMPT = """
Analyze this lab report image and extract ALL test results.

Return ONLY valid JSON in this exact format:
{
  "tests": {
    "hemoglobin": {"value": 14.5, "unit": "g/dL", "reference": "13-17"},
    "glucose_fasting": {"value": 95, "unit": "mg/dL", "reference": "70-100"},
    "cholesterol_total": {"value": 210, "unit": "mg/dL", "reference": "<200"},
    "hdl": {"value": 45, "unit": "mg/dL", "reference": ">40"},
    "ldl": {"value": 130, "unit": "mg/dL", "reference": "<100"},
    "triglycerides": {"value": 150, "unit": "mg/dL", "reference": "<150"}
  }
}

Extract all visible tests. Use snake_case for test names.
If a value is not visible, omit that test.
"""
ANALYSIS_PROMPT = """
You are a medical analysis assistant. Analyze these lab results:

{lab_data}

Patient dietary preferences: {preferences}

Provide analysis in this JSON format:
{{
  "issues": ["list of health issues identified"],
  "risk_factors": ["potential health risks based on values"],
  "recommendations": ["dietary recommendations for improvement"]
}}

Focus on nutritional and dietary aspects. Be specific about which values are concerning.
"""

class OCRService:
    async def process_report(self, file_path: str, preferences: dict) -> tuple[dict, HealthAnalysis]:
        """Process a lab report and extract data with analysis"""
        try:
            images = self._prepare_images(file_path)
            
            all_tests = {}
            for img_path in images:
                print(f"[OCR] Extracting from image: {img_path}")
                extracted = await self._extract_from_image(img_path)
                print(f"[OCR] Extracted tests: {extracted}")
                all_tests.update(extracted)

            lab_data = {}
            for test_name, values in all_tests.items():
                lab_data[test_name] = LabValue(
                    value=values['value'],
                    unit=values['unit'],
                    reference_range=values.get('reference'),
                    status=self._determine_status(values)
                )

            print(f"[OCR] Analyzing {len(lab_data)} tests...")
            analysis = await self._analyze_result(lab_data, preferences)
            print(f"[OCR] Analysis complete: {analysis}")
            return lab_data, analysis
        except Exception as e:
            print(f"[OCR ERROR] {type(e).__name__}: {e}")
            raise

    def _prepare_images(self, file_path: str) -> list[str]:
        """Convert PDF to images or return image path"""

        path = Path(file_path)

        if path.suffix.lower() == '.pdf':
            images = convert_from_path(str(path))
            img_paths = []

            for i, img in enumerate(images):
                img_path = path.parent / f"{path.stem}_{i}.png"
                img.save(str(img_path))
                img_paths.append(str(img_path))

            return img_paths
        else:
            return [str(path)]

    async def _extract_from_image(self, image_path: str) -> dict:
        """Use vision model to extract lab values"""
        response = await ollama.generate_with_image(
            model=settings.vision_model,
            prompt=EXTRACTION_PROMPT,
            image_path=image_path
        )

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('tests', {})
        except json.JSONDecodeError:
            pass

        return {}

    async def _analyze_result(self, lab_data: dict, preferences: dict) -> HealthAnalysis:
        """Analyze lab results for health issues"""
        prompt = ANALYSIS_PROMPT.format(
            lab_data=json.dumps({k: v.model_dump() for k, v in lab_data.items()}),
            preferences=json.dumps(preferences)
        )

        response = await ollama.generate(
            model=settings.text_model,
            prompt=prompt
        )

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return HealthAnalysis(**data)
        except json.JSONDecodeError:
            pass

        return HealthAnalysis()
    
    def _determine_status(self, values: dict) -> str:
        """Determine if value is normal/high/low based on reference"""
        try:
            value = float(values.get("value", 0))
            reference = values.get("reference", "")
        
            if not reference:
                return "unknown"
        
            reference = reference.strip()
        
            # Handle "< X" format (e.g., "<200" for cholesterol)
            if reference.startswith("<"):
                max_val = float(reference[1:].strip())
                return "normal" if value < max_val else "high"
        
            # Handle "> X" format (e.g., ">40" for HDL)
            if reference.startswith(">"):
                min_val = float(reference[1:].strip())
                return "normal" if value > min_val else "low"
        
            # Handle "X-Y" range format (e.g., "13-17" for hemoglobin)
            if "-" in reference:
                parts = reference.split("-")
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
            
                if value < min_val:
                    return "low"
                elif value > max_val:
                    return "high"
                else:
                    return "normal"
        
            # Handle single value (treat as max)
            try:
                max_val = float(reference)
                return "normal" if value <= max_val else "high"
            except ValueError:
                pass
        
            return "unknown"
        
        except (ValueError, TypeError, IndexError):
            return "unknown"

ocr_service = OCRService()