"""ChromaDB vector store manager — per-org collection isolation."""
import chromadb

import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)


class ChromaManager:
    """Singleton manager for ChromaDB vector store with per-org collections."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

    def get_or_create_collection(self, org_id: str):
        """Get or create a dedicated collection for an organization."""
        collection_name = f"jury_ai_{org_id}"
        return self.client.get_or_create_collection(name=collection_name)

    def add_documents(
        self,
        org_id: str,
        doc_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        """Add document chunks and their embeddings to the org's collection."""
        collection = self.get_or_create_collection(org_id)
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        logger.info("chroma_documents_added", org_id=org_id, doc_id=doc_id, chunks=len(chunks))

    def query(
        self, org_id: str, query_embedding: list[float], n_results: int = 3
    ) -> list[str]:
        """Retrieve top matching document chunks by embedding similarity."""
        collection = self.get_or_create_collection(org_id)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        if not results or not results["documents"]:
            return []
        return results["documents"][0]

    def get_full_text(self, org_id: str, doc_id: str, cap: int = 30000) -> str:
        """Reconstruct the full document text from stored chunks.

        Retrieves all chunks for a specific document within an org's collection,
        sorts them by chunk_index, and joins them. Optionally caps the output length.
        """
        collection = self.get_or_create_collection(org_id)
        results = collection.get(where={"doc_id": doc_id})

        if not results or not results["documents"]:
            return ""

        # Sort chunks by their index to reconstruct original order
        paired = zip(results["documents"], results["metadatas"])
        sorted_chunks = sorted(paired, key=lambda x: x[1].get("chunk_index", 0))
        text = "\n".join(chunk for chunk, _ in sorted_chunks)

        return text[:cap] if len(text) > cap else text

    def delete_document(self, org_id: str, doc_id: str) -> None:
        """Delete all chunks related to a specific document."""
        collection = self.get_or_create_collection(org_id)
        collection.delete(where={"doc_id": doc_id})
        logger.info("chroma_document_deleted", org_id=org_id, doc_id=doc_id)
