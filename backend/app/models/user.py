import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.core.constants import UserRole

class User(TimestampMixin, Base):
    __tablename__ = 'users'
    
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('organizations.id'))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default=UserRole.ANALYST)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)
    
    # Relationships
    organization: Mapped['Organization'] = relationship(back_populates='users')
    documents: Mapped[list['Document']] = relationship(back_populates='user')
    queries: Mapped[list['Query']] = relationship(back_populates='user')
