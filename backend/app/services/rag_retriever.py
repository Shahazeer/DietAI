"""
RAG Retriever - Retrieves relevant nutrition knowledge for diet planning
"""

from typing import List, Dict, Optional
from app.services.vector_store import get_vector_store
from app.models.lab_report import HealthAnalysis

class RAGRetriever:
    def __init__(self):
        self.vector_store = get_vector_store()
    
    def retrieve_for_diet_plan(
        self,
        health_analysis: HealthAnalysis,
        preferences: Dict,
        top_k: int = 20  # Increased to account for filtering
    ) -> str:
        """
        Retrieve relevant nutrition knowledge for diet planning
        
        Args:
            health_analysis: User's health conditions
            preferences: Diet preferences (type, allergies, cuisines)
            top_k: Number of documents to retrieve (before filtering)
        
        Returns:
            Formatted string with relevant nutrition knowledge
        """
        # Build query from health issues
        health_issues = ", ".join(health_analysis.issues[:3]) if health_analysis.issues else "general wellness"
        diet_type = preferences.get("type", "non-veg")
        allergies = ", ".join(preferences.get("allergies", [])) or "None"
        cuisines = ", ".join(preferences.get("cuisines", ["Indian"]))
        
        # Query for health-specific knowledge
        query_text = f"foods good for {health_issues}, {diet_type} diet, {cuisines} cuisine"
        
        print(f"[RAG] Retrieving knowledge for: {query_text}")
        
        results = self.vector_store.query(
            query_text=query_text,
            n_results=top_k
        )
        
        if not results['documents']:
            print("[RAG] No documents retrieved, using empty context")
            return ""
        
        # Format retrieved knowledge with diet type filtering
        knowledge_text = self._format_retrieved_knowledge(
            results['documents'],
            results['metadatas'],
            diet_type,
            allergies
        )
        
        print(f"[RAG] Retrieved {len(results['documents'])} documents, filtered to {knowledge_text.count('\\n') - 3} items")
        return knowledge_text
    
    def _format_retrieved_knowledge(
        self,
        documents: List[str],
        metadatas: List[Dict],
        diet_type: str,
        allergies: str
    ) -> str:
        """Format retrieved documents into a readable knowledge base"""
        
        # Filter out allergens if specified
        allergen_list = [a.strip().lower() for a in allergies.split(",") if a.strip().lower() != "none"]
        
        formatted_items = []
        seen_foods = set()
        
        for doc, meta in zip(documents, metadatas):
            food_name = meta.get("food_name", "").lower()
            food_diet_type = meta.get("diet_type", "").lower()
            
            # Skip if already added
            if food_name in seen_foods:
                continue
            
            # Skip if contains allergen
            if any(allergen in food_name for allergen in allergen_list):
                print(f"[RAG] Filtered out allergen: {food_name}")
                continue
            
            # Filter by diet type
            if not self._is_compatible_diet(diet_type, food_diet_type):
                print(f"[RAG] Filtered out {food_name} (diet type: {food_diet_type} not compatible with {diet_type})")
                continue
            
            seen_foods.add(food_name)
            formatted_items.append(doc)
        
        if not formatted_items:
            return ""
        
        # Limit to top items to avoid prompt overflow
        top_items = formatted_items[:10]
        
        knowledge_base = "NUTRITION KNOWLEDGE BASE:\n"
        knowledge_base += "Use ONLY the foods listed below when creating meal plans:\n\n"
        knowledge_base += "\n".join(f"{i+1}. {item}" for i, item in enumerate(top_items))
        knowledge_base += "\n\n"
        
        return knowledge_base
    
    def _is_compatible_diet(self, user_diet: str, food_diet: str) -> bool:
        """
        Check if a food's diet type is compatible with user's diet preference
        
        Compatibility rules:
        - vegetarian: only vegetarian foods
        - vegan: only vegan foods
        - eggetarian: vegetarian + eggs
        - non-veg: all foods
        """
        user_diet = user_diet.lower()
        food_diet = food_diet.lower()
        
        # Non-veg users can eat everything
        if user_diet == "non-veg":
            return True
        
        # Vegetarian users can eat vegetarian foods only
        if user_diet == "vegetarian":
            return food_diet == "vegetarian"
        
        # Vegan users can eat vegan foods only
        if user_diet == "vegan":
            return food_diet == "vegan"
        
        # Eggetarian users can eat vegetarian and eggs
        if user_diet == "eggetarian":
            return food_diet in ["vegetarian", "eggetarian"]
        
        # Default: allow if food is vegetarian (safe default)
        return food_diet == "vegetarian"


# Singleton instance
_rag_retriever = None

def get_rag_retriever() -> RAGRetriever:
    """Get or create RAG retriever singleton"""
    global _rag_retriever
    if _rag_retriever is None:
        _rag_retriever = RAGRetriever()
    return _rag_retriever
