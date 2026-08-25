import uuid
from sqlalchemy import ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Query(TimestampMixin, Base):
    __tablename__ = 'queries'
    
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('documents.id'))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    retrieved_chunks: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_queries_document_time', 'document_id', 'created_at'),
    )
    
    # Relationships
    document: Mapped['Document'] = relationship(back_populates='queries')
    user: Mapped['User'] = relationship(back_populates='queries')
