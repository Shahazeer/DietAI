import logging
from app.services.ollama_client import llm
from app.models.diet_plan import DietPlanResponse, DayPlan, Meal, ProgressReport
from app.models.lab_report import HealthAnalysis
from app.config import settings
from app.services.rag_retriever import get_rag_retriever
from app.utils.llm_utils import extract_json

logger = logging.getLogger(__name__)

DIET_PLAN_PROMPT = """{nutrition_knowledge}You are an expert clinical dietician creating a personalized 7-day meal plan.

PATIENT HEALTH PROFILE:
- Active health issues: {health_issues}
- Risk factors: {risk_factors}
- Lab-based dietary recommendations: {recommendations}

DIETARY CONSTRAINTS — STRICTLY FOLLOW ALL OF THESE:
- Diet type: {diet_type}
- Allergies (NEVER include these ingredients): {allergies}
- Preferred cuisines: {cuisines}
- vegetarian: NO meat, fish, seafood, poultry, or eggs
- vegan: NO animal products at all (no meat, fish, dairy, eggs, honey)
- eggetarian: eggs allowed, NO meat, fish, seafood, or poultry
- non-veg: all foods allowed

{progress_context}
MEAL PLAN RULES:
- Every meal must directly address at least one health issue or risk factor
- Use foods from the nutrition knowledge base above when available
- Vary meals — do not repeat the same meal across days
- Keep ingredients realistic and available in {cuisines} cuisine
- Calorie targets: breakfast 300-400, lunch 400-500, dinner 350-450

Return ONLY valid JSON with no markdown, no explanation, no extra text:
{{"days":[{{"day":1,"breakfast":{{"name":"Meal Name","ingredients":["ingredient1","ingredient2","ingredient3"],"benefits":["addresses issue1","provides nutrient X"],"calories":350}},"lunch":{{"name":"Meal Name","ingredients":["ingredient1","ingredient2","ingredient3"],"benefits":["benefit1","benefit2"],"calories":450}},"dinner":{{"name":"Meal Name","ingredients":["ingredient1","ingredient2","ingredient3"],"benefits":["benefit1","benefit2"],"calories":400}}}}],"rationale":"Explain how this 7-day plan specifically targets the patient's health issues and risk factors"}}

Generate all 7 days."""

PROGRESS_CONTEXT_TEMPLATE = """PREVIOUS PLAN FEEDBACK:
- What improved: {improvements}
- Still needs work: {current_issues}
Build on what worked. Replace meals that did not help the persisting issues.
"""


class DietPlanner:
    def __init__(self):
        self.rag_retriever = get_rag_retriever()

    async def generate_plan(
        self,
        health_analysis: HealthAnalysis,
        preferences: dict,
        progress: ProgressReport | None = None,
    ) -> dict:
        """Generate a personalized 7-day meal plan using RAG + full health context"""

        logger.info("[DIET] Retrieving nutrition knowledge via RAG...")
        nutrition_knowledge = ""
        try:
            nutrition_knowledge = self.rag_retriever.retrieve_for_diet_plan(
                health_analysis=health_analysis,
                preferences=preferences,
                top_k=15,
            )
        except Exception as e:
            logger.warning("[DIET] RAG retrieval failed, continuing without it: %s", e)

        progress_context = ""
        if progress:
            improvements = ", ".join(progress.improvements) or "None yet"
            current_issues = ", ".join(progress.current_issues) or "None"
            progress_context = PROGRESS_CONTEXT_TEMPLATE.format(
                improvements=improvements,
                current_issues=current_issues,
            )

        # Use ALL health analysis fields — not just issues[:3]
        health_issues = "; ".join(health_analysis.issues) if health_analysis.issues else "General wellness"
        risk_factors = "; ".join(health_analysis.risk_factors) if health_analysis.risk_factors else "None identified"
        recommendations = "; ".join(health_analysis.recommendations) if health_analysis.recommendations else "Balanced nutrition"

        prompt = DIET_PLAN_PROMPT.format(
            nutrition_knowledge=nutrition_knowledge + "\n" if nutrition_knowledge else "",
            health_issues=health_issues,
            risk_factors=risk_factors,
            recommendations=recommendations,
            diet_type=preferences.get("type", "non-veg"),
            allergies=", ".join(preferences.get("allergies", [])) or "None",
            cuisines=", ".join(preferences.get("cuisines", ["Indian"])) or "Indian",
            progress_context=progress_context,
        )

        logger.info(
            "[DIET] Generating plan with %s — issues: %d, risks: %d, recs: %d",
            settings.text_model,
            len(health_analysis.issues),
            len(health_analysis.risk_factors),
            len(health_analysis.recommendations),
        )

        response = await llm.generate(
            model=settings.text_model,
            prompt=prompt,
            num_predict=8192,
        )
        logger.info("[DIET] Response received (%d chars), parsing...", len(response))

        try:
            result = extract_json(response, "[DIET]")
            days_count = len(result.get("days", []))
            logger.info("[DIET] Successfully parsed %d days", days_count)
            if days_count > 0:
                return result
            logger.warning("[DIET] Parsed JSON has no days. Response preview:\n%s", response[:1000])
        except ValueError as e:
            logger.error("%s", e)
        except Exception as e:
            logger.error("[DIET] Unexpected error parsing response: %s", e)

        return {
            "days": [],
            "rationale": "Failed to generate meal plan — model response was incomplete. Please try again.",
        }


diet_planner = DietPlanner()
