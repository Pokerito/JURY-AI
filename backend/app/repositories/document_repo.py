from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundException
from app.core.constants import DocumentStatus

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(Document, session)
    
    async def list_by_org(self, org_id: UUID, offset: int = 0, limit: int = 20, include_deleted: bool = False) -> tuple[list[Document], int]:
        """List documents for an organization, optionally including soft-deleted ones."""
        stmt = select(Document).where(Document.org_id == org_id)
        count_stmt = select(func.count()).select_from(Document).where(Document.org_id == org_id)
        
        if not include_deleted:
            stmt = stmt.where(Document.is_deleted == False)
            count_stmt = count_stmt.where(Document.is_deleted == False)
            
        stmt = stmt.order_by(Document.created_at.desc()).offset(offset).limit(limit)
        
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
    
    async def soft_delete(self, doc_id: UUID) -> Document:
        """Mark a document as deleted instead of removing it from the database."""
        doc = await self.get_by_id(doc_id)
        if not doc:
            raise NotFoundException(f"Document with id {doc_id} not found")
        
        doc.is_deleted = True
        await self.session.commit()
        await self.session.refresh(doc)
        return doc
    
    async def update_status(self, doc_id: UUID, status: str) -> Document:
        """Update the processing status of a document."""
        return await self.update(doc_id, status=status)
