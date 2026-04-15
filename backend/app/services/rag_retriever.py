"""
RAG Retriever — retrieves relevant nutrition knowledge for diet planning.
"""

import logging
from app.services.vector_store import get_vector_store
from app.models.lab_report import HealthAnalysis

logger = logging.getLogger(__name__)


class RAGRetriever:
    def __init__(self):
        self.vector_store = get_vector_store()

    def retrieve_for_diet_plan(
        self,
        health_analysis: HealthAnalysis,
        preferences: dict,
        top_k: int = 20,
    ) -> str:
        """Retrieve relevant nutrition knowledge for diet planning."""
        health_issues = ", ".join(health_analysis.issues) if health_analysis.issues else "general wellness"
        risk_factors = ", ".join(health_analysis.risk_factors) if health_analysis.risk_factors else ""
        diet_type = preferences.get("type", "non-veg")
        allergies = ", ".join(preferences.get("allergies", [])) or "None"
        cuisines = ", ".join(preferences.get("cuisines", ["Indian"]))

        health_context = f"{health_issues}, {risk_factors}".strip(", ") if risk_factors else health_issues
        query_text = f"foods good for {health_context}, {diet_type} diet, {cuisines} cuisine"

        logger.info("[RAG] Retrieving knowledge for: %s", query_text)

        results = self.vector_store.query(query_text=query_text, n_results=top_k)

        if not results["documents"]:
            logger.info("[RAG] No documents retrieved, using empty context")
            return ""

        knowledge_text = self._format_retrieved_knowledge(
            results["documents"],
            results["metadatas"],
            diet_type,
            allergies,
        )

        logger.info("[RAG] Retrieved %d documents", len(results["documents"]))
        return knowledge_text

    def _format_retrieved_knowledge(
        self,
        documents: list[str],
        metadatas: list[dict],
        diet_type: str,
        allergies: str,
    ) -> str:
        """Format retrieved documents into a readable knowledge base."""
        allergen_list = [a.strip().lower() for a in allergies.split(",") if a.strip().lower() != "none"]

        formatted_items = []
        seen_foods: set[str] = set()

        for doc, meta in zip(documents, metadatas):
            food_name = meta.get("food_name", "").lower()
            food_diet_type = meta.get("diet_type", "").lower()

            if food_name in seen_foods:
                continue
            if any(allergen in food_name for allergen in allergen_list):
                logger.debug("[RAG] Filtered out allergen: %s", food_name)
                continue
            if not self._is_compatible_diet(diet_type, food_diet_type):
                logger.debug("[RAG] Filtered out %s (diet type: %s)", food_name, food_diet_type)
                continue

            seen_foods.add(food_name)
            formatted_items.append(doc)

        if not formatted_items:
            return ""

        top_items = formatted_items[:10]
        lines = ["NUTRITION KNOWLEDGE BASE:", "Use ONLY the foods listed below when creating meal plans:", ""]
        lines.extend(f"{i + 1}. {item}" for i, item in enumerate(top_items))
        lines.append("")
        return "\n".join(lines)

    def _is_compatible_diet(self, user_diet: str, food_diet: str) -> bool:
        """Check if a food's diet type is compatible with the user's diet preference."""
        user_diet = user_diet.lower()
        food_diet = food_diet.lower()

        if user_diet == "non-veg":
            return True
        if user_diet == "vegetarian":
            return food_diet == "vegetarian"
        if user_diet == "vegan":
            return food_diet == "vegan"
        if user_diet == "eggetarian":
            return food_diet in ("vegetarian", "eggetarian")
        return food_diet == "vegetarian"


_rag_retriever: RAGRetriever | None = None


def get_rag_retriever() -> RAGRetriever:
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever()
    return _rag_retriever
