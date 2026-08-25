import uuid
from sqlalchemy import String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from app.core.constants import DocumentStatus

class Document(TimestampMixin, Base):
    __tablename__ = 'documents'
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('organizations.id'))
    filename: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(10))  # pdf|docx|txt
    file_size_bytes: Mapped[int] = mapped_column()
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default=DocumentStatus.UPLOADED)
    raw_text_preview: Mapped[str | None] = mapped_column(Text, nullable=True)  # first 500 chars
    chunk_count: Mapped[int] = mapped_column(default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_documents_org_listing', 'org_id', 'is_deleted', 'created_at'),
        Index('ix_documents_user', 'user_id'),
        Index('ix_documents_status', 'status'),
    )
    
    # Relationships
    user: Mapped['User'] = relationship(back_populates='documents')
    organization: Mapped['Organization'] = relationship(back_populates='documents')
    analyses: Mapped[list['Analysis']] = relationship(back_populates='document', cascade='all, delete-orphan')
    queries: Mapped[list['Query']] = relationship(back_populates='document', cascade='all, delete-orphan')
