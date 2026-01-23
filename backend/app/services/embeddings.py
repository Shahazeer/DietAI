"""
Embedding service using sentence-transformers
Generates embeddings for nutrition knowledge and queries
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        model_name: Lightweight model good for semantic search (384 dimensions)
        """
        print(f"[EMBEDDING] Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"[EMBEDDING] Model loaded successfully!")
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def encode_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()


# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
