from typing import Generic, TypeVar, Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: UUID) -> T | None:
        """Get a record by its UUID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, id: UUID, **kwargs) -> T:
        """Update an existing record by its UUID."""
        instance = await self.get_by_id(id)
        if not instance:
            raise NotFoundException(f"{self.model.__name__} with id {id} not found")
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def delete(self, id: UUID) -> None:
        """Delete a record by its UUID."""
        instance = await self.get_by_id(id)
        if not instance:
            raise NotFoundException(f"{self.model.__name__} with id {id} not found")
        await self.session.delete(instance)
        await self.session.commit()
    
    async def list(self, filters: dict[str, Any] | None = None, offset: int = 0, limit: int = 20) -> tuple[list[T], int]:
        """List records with optional filters, pagination, and total count."""
        stmt = select(self.model)
        count_stmt = select(func.count()).select_from(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    condition = getattr(self.model, key) == value
                    stmt = stmt.where(condition)
                    count_stmt = count_stmt.where(condition)
                    
        stmt = stmt.offset(offset).limit(limit)
        
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()
        
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
