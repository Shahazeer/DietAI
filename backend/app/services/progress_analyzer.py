import json
import re
from typing import Optional
from app.services.ollama_client import ollama
from app.models.diet_plan import ProgressReport
from app.config import settings

PROGRESS_PROMPT = """
Compare these two lab reports to evaluate diet plan effectiveness.

PREVIOUS LAB REPORT (before diet plan):
{previous_report}

CURRENT LAB REPORT (after diet plan):
{current_report}

DIET PLAN THAT WAS FOLLOWED:
{diet_plan}

Analyze the changes and provide a progress report in this JSON format:
{{
  "previous_issues": ["issues from previous report"],
  "current_issues": ["issues still present or new"],
  "improvements": ["specific metrics that improved with % change"],
  "deteriorations": ["metrics that got worse with % change"],
  "effectiveness_score": 75,
  "summary": "Brief summary of overall progress"
}}

Be specific about numerical changes (e.g., "Cholesterol reduced from 220 to 195 mg/dL (-11%)")
Score from 0-100 based on how much the diet helped.
"""

class ProgressAnalyzer:
    async def analyze_progress(
        self,
        previous_report: dict,
        current_report: dict,
        diet_plan: list
    ) -> ProgressReport:
        """Compare two reports to measure diet effectiveness"""

        prompt = PROGRESS_PROMPT.format(
            previous_report=json.dumps(previous_report.get("extracted_data", {})),
            current_report=json.dumps(current_report.get("extracted_data", {})),
            diet_plan=json.dumps(diet_plan)
        )

        response = await ollama.generate(
            model=settings.text_model,
            prompt=prompt
        )

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return ProgressReport(
                    previous_issues=data.get("previous_issues", []),
                    current_issues=data.get("current_issues", []),
                    improvements=data.get("improvements", []),
                    deteriorations=data.get("deteriorations", []),
                    effectiveness_score=data.get("effectiveness_score", 0)
                )
        except (json.JSONDecodeError, Exception):
            pass

        return ProgressReport(
            previous_issues=[],
            current_issues=[],
            improvements=[],
            deteriorations=[],
            effectiveness_score=0
        )

progress_analyzer = ProgressAnalyzer()
