"""Risk analysis service — clause detection, risk scoring, and safer alternatives."""
import json
import re
import time
import asyncio
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis, RiskClause
from app.repositories.analysis_repo import AnalysisRepository
from app.integrations.gemini_client import GeminiClient
from app.integrations.chroma_client import ChromaManager
from app.core.constants import AnalysisType, RISK_SCORE_WEIGHTS
from app.core.exceptions import NotFoundException

logger = structlog.get_logger(__name__)


class RiskAnalysisService:
    def __init__(self, session: AsyncSession, gemini: GeminiClient, chroma: ChromaManager):
        self.session = session
        self.gemini = gemini
        self.chroma = chroma
        self.analysis_repo = AnalysisRepository(session)

    @staticmethod
    def _calculate_safety_score(clauses: list[dict]) -> int:
        """Calculate safety score from 0-100 based on clause risk levels."""
        score = 100
        for clause in clauses:
            risk = str(clause.get("risk_level", "low")).lower()
            score -= RISK_SCORE_WEIGHTS.get(risk, 0)
        return max(0, score)

    @staticmethod
    def _clean_json_response(text: str) -> str:
        """Strip markdown code fences from LLM JSON output."""
        cleaned = re.sub(r"```json\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        return cleaned.strip()

    async def analyze_risk(
        self, doc_id: UUID, org_id: UUID, idempotency_key: str | None = None
    ) -> Analysis:
        """Run full risk analysis on a document. Idempotent if key is provided."""
        # Check idempotency
        if idempotency_key:
            existing = await self.analysis_repo.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info("idempotent_hit", key=idempotency_key)
                return existing

        start_time = time.monotonic()

        # Get full document text from ChromaDB with fallback to document preview
        full_text = self.chroma.get_full_text(str(org_id), str(doc_id), cap=30000)
        if not full_text:
            from app.repositories.document_repo import DocumentRepository
            doc_repo = DocumentRepository(self.session)
            doc = await doc_repo.get_by_id(doc_id)
            if doc and doc.raw_text_preview:
                full_text = doc.raw_text_preview
            else:
                raise NotFoundException("Document content not found")

        prompt = f"""You are a legal risk algorithm. Analyze the document context below.
Identify ALL clauses and classify their risk. Return ONLY a pure JSON array. No markdown. No code blocks. JUST THE RAW JSON ARRAY.
Format:
[
  {{
    "clause_name": "Short name for the clause",
    "risk_level": "Critical" | "High" | "Medium" | "Low",
    "justification": "Brief reason for this risk level",
    "safer_alternative": "For Critical/High only: a fairer alternative clause wording. For Medium/Low: null"
  }}
]
Include ALL clauses you find — even safe ones with "Low" rating.

Context:
{full_text}"""

        # Generate via Gemini (sync call wrapped in thread)
        raw_response = await asyncio.to_thread(self.gemini.generate_content, prompt)
        cleaned = self._clean_json_response(raw_response)

        # Parse JSON
        all_clauses: list[dict] = []
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                all_clauses = parsed
        except json.JSONDecodeError:
            logger.warning("risk_json_parse_failed", raw=cleaned[:200])

        safety_score = self._calculate_safety_score(all_clauses)
        processing_time_ms = int((time.monotonic() - start_time) * 1000)

        # Determine model used
        model_used = "gemini-2.5-flash"

        # Persist analysis + clauses
        analysis_data = {
            "document_id": doc_id,
            "analysis_type": AnalysisType.RISK_SCORE.value,
            "result": {"all_clauses": all_clauses},
            "safety_score": safety_score,
            "processing_time_ms": processing_time_ms,
            "model_used": model_used,
            "idempotency_key": idempotency_key,
        }

        clause_dicts = [
            {
                "clause_name": c.get("clause_name", "Unknown"),
                "risk_level": c.get("risk_level", "low").lower(),
                "justification": c.get("justification", ""),
                "safer_alternative": c.get("safer_alternative"),
                "sort_order": idx,
            }
            for idx, c in enumerate(all_clauses)
        ]

        analysis = await self.analysis_repo.create_with_clauses(analysis_data, clause_dicts)

        logger.info(
            "risk_analysis_complete",
            doc_id=str(doc_id),
            score=safety_score,
            clauses=len(all_clauses),
            duration_ms=processing_time_ms,
        )

        return analysis

    async def get_risk_score(self, doc_id: UUID, org_id: UUID) -> dict:
        """Get the latest risk analysis for a document, running analysis if not yet performed."""
        analyses = await self.analysis_repo.get_by_document(
            doc_id, AnalysisType.RISK_SCORE.value
        )
        if not analyses:
            latest = await self.analyze_risk(doc_id=doc_id, org_id=org_id)
        else:
            latest = sorted(analyses, key=lambda a: a.created_at, reverse=True)[0]

        # Build response with clause data
        checklist = [
            {
                "clause_name": c.clause_name,
                "risk_level": c.risk_level,
                "justification": c.justification,
                "safer_alternative": c.safer_alternative,
                "sort_order": c.sort_order,
            }
            for c in latest.risk_clauses
            if c.risk_level in ("critical", "high")
        ]

        all_clauses = [
            {
                "clause_name": c.clause_name,
                "risk_level": c.risk_level,
                "justification": c.justification,
                "safer_alternative": c.safer_alternative,
                "sort_order": c.sort_order,
            }
            for c in latest.risk_clauses
        ]

        return {
            "score": latest.safety_score,
            "checklist": checklist,
            "all_clauses": all_clauses,
        }
