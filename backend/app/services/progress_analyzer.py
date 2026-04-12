import json
import re
import logging
from typing import Optional
from app.services.ollama_client import llm
from app.models.diet_plan import ProgressReport
from app.config import settings

logger = logging.getLogger(__name__)

PROGRESS_PROMPT = """You are a clinical dietician evaluating whether a diet plan improved a patient's lab results.

PREVIOUS LAB REPORT (before diet plan):
{previous_report}

CURRENT LAB REPORT (after following the diet plan):
{current_report}

DIET PLAN THAT WAS FOLLOWED:
{diet_plan}

Compare the two reports value by value. Identify what changed, improved, or got worse.

Return ONLY valid JSON with no other text:
{{
  "previous_issues": ["High LDL cholesterol (130 mg/dL)", "Low hemoglobin (10 g/dL)"],
  "current_issues": ["LDL still elevated (115 mg/dL)", "Hemoglobin improved but still borderline"],
  "improvements": ["Hemoglobin increased from 10 to 12.5 g/dL (+25%)", "Triglycerides reduced from 200 to 160 mg/dL (-20%)"],
  "deteriorations": ["Blood glucose increased from 95 to 108 mg/dL (+13.7%)"],
  "effectiveness_score": 72,
  "summary": "The diet plan was moderately effective. Iron levels improved significantly, likely due to increased lentil and spinach intake. LDL reduction was modest. Blood glucose warrants attention."
}}

effectiveness_score: 0-100 based on overall improvement. Be specific with numbers and percentages."""


class ProgressAnalyzer:
    async def analyze_progress(
        self,
        previous_report: dict,
        current_report: dict,
        diet_plan: list,
    ) -> ProgressReport:
        """Compare two lab reports to measure diet plan effectiveness"""

        prompt = PROGRESS_PROMPT.format(
            previous_report=json.dumps(previous_report.get("extracted_data", {}), indent=2),
            current_report=json.dumps(current_report.get("extracted_data", {}), indent=2),
            diet_plan=json.dumps(diet_plan, indent=2),
        )

        try:
            response = await llm.generate(model=settings.text_model, prompt=prompt)
            logger.debug("[PROGRESS] Raw response: %s", response[:500])

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return ProgressReport(
                    previous_issues=data.get("previous_issues", []),
                    current_issues=data.get("current_issues", []),
                    improvements=data.get("improvements", []),
                    deteriorations=data.get("deteriorations", []),
                    effectiveness_score=data.get("effectiveness_score", 0),
                    summary=data.get("summary", ""),
                )

            logger.warning("[PROGRESS] No JSON found in response:\n%s", response)
        except json.JSONDecodeError as e:
            logger.error("[PROGRESS] JSON parse error: %s", e)
        except Exception as e:
            logger.error("[PROGRESS] Unexpected error: %s", e)

        return ProgressReport(
            previous_issues=[],
            current_issues=[],
            improvements=[],
            deteriorations=[],
            effectiveness_score=0,
            summary="Progress analysis failed — please try again.",
        )


progress_analyzer = ProgressAnalyzer()
