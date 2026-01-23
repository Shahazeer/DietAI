"""
Vector store service using ChromaDB
Stores and retrieves nutrition knowledge
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
from app.services.embeddings import get_embedding_service

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """Initialize ChromaDB with persistence"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        print(f"[VECTOR_STORE] Initializing ChromaDB at {persist_directory}...")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="nutrition_knowledge",
            metadata={"description": "Nutrition facts and health-food relationships"}
        )
        
        self.embedding_service = get_embedding_service()
        print(f"[VECTOR_STORE] Initialized with {self.collection.count()} documents")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Add documents to the vector store"""
        if not documents:
            return
        
        # Generate IDs if not provided
        if ids is None:
            current_count = self.collection.count()
            ids = [f"doc_{current_count + i}" for i in range(len(documents))]
        
        # Generate embeddings
        print(f"[VECTOR_STORE] Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_service.encode(documents)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[VECTOR_STORE] Added {len(documents)} documents. Total: {self.collection.count()}")
    
    def query(
        self,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the vector store for relevant documents
        
        Args:
            query_text: The search query
            n_results: Number of results to return
            where: Metadata filters (e.g., {"category": "vegetable"})
        
        Returns:
            Dict with 'documents', 'metadatas', 'distances'
        """
        # Generate query embedding
        query_embedding = self.embedding_service.encode_single(query_text)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return {
            "documents": results['documents'][0] if results['documents'] else [],
            "metadatas": results['metadatas'][0] if results['metadatas'] else [],
            "distances": results['distances'][0] if results['distances'] else []
        }
    
    def clear(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(name="nutrition_knowledge")
        self.collection = self.client.get_or_create_collection(
            name="nutrition_knowledge",
            metadata={"description": "Nutrition facts and health-food relationships"}
        )
        print("[VECTOR_STORE] Collection cleared")
    
    def get_count(self) -> int:
        """Get number of documents in the store"""
        return self.collection.count()


# Singleton instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get or create vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
