from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> User | None:
        """Get a user by their email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_org(self, org_id: UUID, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        """Get all users belonging to an organization."""
        return await self.list(filters={"organization_id": org_id}, offset=offset, limit=limit)
    
    async def update_last_login(self, user_id: UUID) -> None:
        """Update the last login timestamp for a user."""
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(UTC)
            await self.session.commit()
