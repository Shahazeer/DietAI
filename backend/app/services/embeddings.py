"""
Embedding service using sentence-transformers.
Generates embeddings for nutrition knowledge and queries.
"""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info("[EMBEDDING] Loading model: %s", model_name)
        self.model = SentenceTransformer(model_name)
        logger.info("[EMBEDDING] Model loaded successfully")

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def encode_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()


_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
