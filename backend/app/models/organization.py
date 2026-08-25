import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Organization(TimestampMixin, Base):
    __tablename__ = 'organizations'
    
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(50), default='free')  # free|pro|enterprise
    
    # Relationships
    users: Mapped[list['User']] = relationship(back_populates='organization')
    documents: Mapped[list['Document']] = relationship(back_populates='organization')
