import json
import re
from datetime import datetime, timedelta
from typing import Optional
from app.services.ollama_client import ollama
from app.models.diet_plan import DietPlanResponse, DayPlan, Meal, ProgressReport
from app.models.lab_report import HealthAnalysis
from app.config import settings

DIET_PLAN_PROMPT = """You are an expert dietician. Create a 7-day meal plan for these health issues:
{health_issues}

Diet: {diet_type} | Allergies: {allergies} | Cuisine: {cuisines}

Return ONLY valid JSON (no extra text):
{{"days":[{{"day":1,"breakfast":{{"name":"...","ingredients":["..."],"benefits":["..."],"calories":300}},"lunch":{{"name":"...","ingredients":["..."],"benefits":["..."],"calories":400}},"dinner":{{"name":"...","ingredients":["..."],"benefits":["..."],"calories":400}}}}],"rationale":"..."}}

Keep ingredient lists short (3-5 items). Keep benefits brief (2-3 items). Include all 7 days."""

PROGRESS_CONTEXT = """
Previous plan results: Improvements: {improvements} | Still issues: {current_issues}
Focus on foods that worked, replace what didn't."""

class DietPlanner:
    async def generate_plan(self, health_analysis: HealthAnalysis, preferences: dict, progress: Optional[ProgressReport] = None) -> dict:
        """Generate a personalized 7-day meal plan"""
        progress_context = ""
        if progress:
            progress_context = PROGRESS_CONTEXT.format(
                improvements=", ".join(progress.improvements) or "None",
                current_issues=", ".join(progress.current_issues) or "None"
            )

        prompt = DIET_PLAN_PROMPT.format(
            health_issues=", ".join(health_analysis.issues[:3]) if health_analysis.issues else "General wellness",
            diet_type=preferences.get("type", "non-veg"),
            allergies=", ".join(preferences.get("allergies", [])) or "None",
            cuisines=", ".join(preferences.get("cuisines", ["Indian"])) or "Indian",
        )
        if progress_context:
            prompt += "\n" + progress_context

        print(f"[DIET] Generating meal plan with {settings.text_model}...")
        response = await ollama.generate(
            model=settings.text_model,
            prompt=prompt,
            num_predict=8192  # Increased for full 7-day plan
        )
        print(f"[DIET] Response received ({len(response)} chars), parsing JSON...")

        try:
            # Try to find and parse JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                days_count = len(result.get('days', []))
                print(f"[DIET] Successfully parsed {days_count} days")
                if days_count > 0:
                    return result
        except Exception as e:
            print(f"[DIET ERROR] Failed to parse response: {e}")
            print(f"[DIET] Raw response preview: {response[:300]}...")

        return {"days": [], "rationale": "Failed to generate meal plan. The AI model response was incomplete. Please try again."}

diet_planner = DietPlanner()