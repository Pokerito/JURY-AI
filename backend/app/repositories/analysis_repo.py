from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis import Analysis, RiskClause
from app.repositories.base import BaseRepository

class AnalysisRepository(BaseRepository[Analysis]):
    def __init__(self, session: AsyncSession):
        super().__init__(Analysis, session)
    
    async def get_by_document(self, doc_id: UUID, analysis_type: str | None = None) -> list[Analysis]:
        """Get all analyses for a specific document, optionally filtered by type."""
        stmt = select(Analysis).options(selectinload(Analysis.risk_clauses)).where(Analysis.document_id == doc_id)
        if analysis_type:
            stmt = stmt.where(Analysis.analysis_type == analysis_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_idempotency_key(self, key: str) -> Analysis | None:
        """Find an analysis by its idempotency key."""
        stmt = select(Analysis).where(Analysis.idempotency_key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_with_clauses(self, analysis_data: dict, clauses: list[dict]) -> Analysis:
        """Create an analysis record along with its associated risk clauses."""
        analysis = Analysis(**analysis_data)
        self.session.add(analysis)
        
        # Flush to get the analysis.id generated
        await self.session.flush()
        
        for clause_data in clauses:
            clause = RiskClause(analysis_id=analysis.id, **clause_data)
            self.session.add(clause)
            
        await self.session.commit()
        stmt = select(Analysis).options(selectinload(Analysis.risk_clauses)).where(Analysis.id == analysis.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
