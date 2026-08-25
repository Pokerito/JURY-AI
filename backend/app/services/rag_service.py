"""RAG query service — embed questions, retrieve context, generate grounded answers."""
import time
import asyncio
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query import Query
from app.integrations.gemini_client import GeminiClient
from app.integrations.chroma_client import ChromaManager

logger = structlog.get_logger(__name__)


class RAGQueryService:
    def __init__(self, session: AsyncSession, gemini: GeminiClient, chroma: ChromaManager):
        self.session = session
        self.gemini = gemini
        self.chroma = chroma

    async def query(
        self, doc_id: UUID, org_id: UUID, user_id: UUID, question: str
    ) -> Query:
        """Run a RAG query: embed question → retrieve chunks → generate answer."""
        start_time = time.monotonic()

        # 1. Embed the question (sync → thread)
        question_embedding = await asyncio.to_thread(
            self.gemini.embed_text, question
        )

        # 2. Retrieve top-3 chunks from ChromaDB (scoped to org_id)
        chunks = self.chroma.query(str(org_id), question_embedding, n_results=3)
        context_text = "\n---\n".join(chunks) if chunks else "No relevant context found."

        # 3. Build prompt with retrieved context
        prompt = f"""You are a Legal AI Assistant. Answer the user's question accurately using only the Context provided.
If the context doesn't contain enough information, say so honestly.

Context:
{context_text}

Question: {question}"""

        # 4. Generate answer via Gemini (sync → thread)
        answer = await asyncio.to_thread(self.gemini.generate_content, prompt)

        processing_time_ms = int((time.monotonic() - start_time) * 1000)

        # 5. Save query record to DB
        new_query = Query(
            document_id=doc_id,
            user_id=user_id,
            question=question,
            answer=answer,
            retrieved_chunks={"chunks": chunks, "count": len(chunks)},
            processing_time_ms=processing_time_ms,
        )
        self.session.add(new_query)
        await self.session.flush()
        await self.session.refresh(new_query)

        logger.info(
            "rag_query_complete",
            doc_id=str(doc_id),
            chunks_retrieved=len(chunks),
            duration_ms=processing_time_ms,
        )

        return new_query
