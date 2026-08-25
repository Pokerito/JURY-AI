"""Entity extraction service — extracts parties, dates, amounts, jurisdictions from legal docs."""
import json
import re
import time
import asyncio
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.repositories.analysis_repo import AnalysisRepository
from app.integrations.gemini_client import GeminiClient
from app.integrations.chroma_client import ChromaManager
from app.core.constants import AnalysisType
from app.core.exceptions import NotFoundException

logger = structlog.get_logger(__name__)


class EntityExtractionService:
    def __init__(self, session: AsyncSession, gemini: GeminiClient, chroma: ChromaManager):
        self.session = session
        self.gemini = gemini
        self.chroma = chroma
        self.analysis_repo = AnalysisRepository(session)

    async def extract_entities(self, doc_id: UUID, org_id: UUID) -> dict:
        """Extract named entities (parties, dates, amounts, jurisdictions) from a document."""
        start_time = time.monotonic()

        # Get full text from ChromaDB with fallback to document preview
        full_text = self.chroma.get_full_text(str(org_id), str(doc_id), cap=8000)
        if not full_text:
            from app.repositories.document_repo import DocumentRepository
            doc_repo = DocumentRepository(self.session)
            doc = await doc_repo.get_by_id(doc_id)
            if doc and doc.raw_text_preview:
                full_text = doc.raw_text_preview
            else:
                raise NotFoundException("Document content not found")

        prompt = f"""Extract key named entities from this legal document. Return ONLY raw JSON, no markdown, no code blocks.
Use exactly this format:
{{
  "parties": ["list of company or person names who are parties to this agreement"],
  "dates": ["list of dates, time periods, or durations mentioned"],
  "amounts": ["list of monetary amounts, fees, or financial figures"],
  "jurisdictions": ["list of jurisdictions, governing law, courts, or arbitration locations"]
}}
If none found for a category, use an empty array [].

Document:
{full_text}"""

        raw = await asyncio.to_thread(self.gemini.generate_content, prompt)

        # Clean and parse JSON
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*", "", cleaned).strip()

        processing_time_ms = int((time.monotonic() - start_time) * 1000)

        try:
            entities = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("entity_json_parse_failed", raw=cleaned[:200])
            entities = {"parties": [], "dates": [], "amounts": [], "jurisdictions": []}

        # Ensure all expected keys exist
        for key in ("parties", "dates", "amounts", "jurisdictions"):
            if key not in entities:
                entities[key] = []

        # Save as Analysis record
        await self.analysis_repo.create(
            document_id=doc_id,
            analysis_type=AnalysisType.ENTITIES.value,
            result=entities,
            processing_time_ms=processing_time_ms,
            model_used="gemini-2.5-flash",
        )

        logger.info(
            "entities_extracted",
            doc_id=str(doc_id),
            parties=len(entities.get("parties", [])),
            duration_ms=processing_time_ms,
        )

        return entities
