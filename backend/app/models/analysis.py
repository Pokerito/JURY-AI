import uuid
from sqlalchemy import String, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Analysis(TimestampMixin, Base):
    __tablename__ = 'analyses'
    
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('documents.id'))
    analysis_type: Mapped[str] = mapped_column(String(20))  # summary|entities|risk_score|full
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    safety_score: Mapped[int | None] = mapped_column(nullable=True)  # 0-100
    processing_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_analyses_document', 'document_id'),
        Index('ix_analyses_idempotency', 'idempotency_key', unique=True),
    )
    
    # Relationships
    document: Mapped['Document'] = relationship(back_populates='analyses')
    risk_clauses: Mapped[list['RiskClause']] = relationship(back_populates='analysis', cascade='all, delete-orphan')

class RiskClause(Base):
    __tablename__ = 'risk_clauses'
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('analyses.id'))
    clause_name: Mapped[str] = mapped_column(String(255))
    risk_level: Mapped[str] = mapped_column(String(20))
    justification: Mapped[str] = mapped_column(Text)
    safer_alternative: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    
    # Relationship
    analysis: Mapped['Analysis'] = relationship(back_populates='risk_clauses')
