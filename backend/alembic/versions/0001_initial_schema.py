"""Initial schema — organizations, users, documents, analyses, risk_clauses, queries

Revision ID: 0001
Revises: None
Create Date: 2024-08-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Organizations ────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # ── Users ────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("org_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="analyst"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_org_id", "users", ["org_id"])

    # ── Documents ────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("org_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="uploaded"),
        sa.Column("raw_text_preview", sa.Text(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_org_listing", "documents", ["org_id", "is_deleted", "created_at"])
    op.create_index("ix_documents_user", "documents", ["user_id"])
    op.create_index("ix_documents_status", "documents", ["status"])

    # ── Analyses ─────────────────────────────────────────────────────────
    op.create_table(
        "analyses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("analysis_type", sa.String(20), nullable=False),
        sa.Column("result", JSON(), nullable=True),
        sa.Column("safety_score", sa.Integer(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("idempotency_key", sa.String(100), unique=True, nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_analyses_document", "analyses", ["document_id"])
    op.create_index("ix_analyses_idempotency", "analyses", ["idempotency_key"], unique=True)

    # ── Risk Clauses ─────────────────────────────────────────────────────
    op.create_table(
        "risk_clauses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("analysis_id", UUID(as_uuid=True), sa.ForeignKey("analyses.id"), nullable=False),
        sa.Column("clause_name", sa.String(255), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("safer_alternative", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_risk_clauses_analysis", "risk_clauses", ["analysis_id"])

    # ── Queries (RAG Q&A history) ────────────────────────────────────────
    op.create_table(
        "queries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("retrieved_chunks", JSON(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_queries_document_time", "queries", ["document_id", "created_at"])


def downgrade() -> None:
    op.drop_table("queries")
    op.drop_table("risk_clauses")
    op.drop_table("analyses")
    op.drop_table("documents")
    op.drop_table("users")
    op.drop_table("organizations")
