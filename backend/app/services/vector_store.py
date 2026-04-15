"""
Vector store service using ChromaDB.
Stores and retrieves nutrition knowledge.
"""

import logging
import chromadb
from pathlib import Path
from app.services.embeddings import get_embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info("[VECTOR_STORE] Initializing ChromaDB at %s", persist_directory)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name="nutrition_knowledge",
            metadata={"description": "Nutrition facts and health-food relationships"},
        )
        self.embedding_service = get_embedding_service()
        logger.info("[VECTOR_STORE] Initialized with %d documents", self.collection.count())

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str] | None = None,
    ) -> None:
        """Add documents to the vector store."""
        if not documents:
            return

        if ids is None:
            current_count = self.collection.count()
            ids = [f"doc_{current_count + i}" for i in range(len(documents))]

        logger.info("[VECTOR_STORE] Generating embeddings for %d documents", len(documents))
        embeddings = self.embedding_service.encode(documents)
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info("[VECTOR_STORE] Added %d documents. Total: %d", len(documents), self.collection.count())

    def query(
        self,
        query_text: str,
        n_results: int = 10,
        where: dict | None = None,
    ) -> dict:
        """Query the vector store for relevant documents."""
        query_embedding = self.embedding_service.encode_single(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(name="nutrition_knowledge")
        self.collection = self.client.get_or_create_collection(
            name="nutrition_knowledge",
            metadata={"description": "Nutrition facts and health-food relationships"},
        )
        logger.info("[VECTOR_STORE] Collection cleared")

    def get_count(self) -> int:
        return self.collection.count()


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
