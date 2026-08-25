"""Document service — upload, parse, embed, and manage legal documents."""
import os
import asyncio
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repo import DocumentRepository
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException
from app.core.constants import DocumentStatus, UserRole
from app.config import get_settings
from app.integrations.gemini_client import GeminiClient
from app.integrations.chroma_client import ChromaManager
from app.integrations.s3_client import StorageClient

# Import the file parser
try:
    from app.services.file_parser import parse_file
except ImportError:
    from services.file_parser import parse_file

logger = structlog.get_logger(__name__)

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


class DocumentService:
    def __init__(
        self,
        session: AsyncSession,
        gemini: GeminiClient,
        chroma: ChromaManager,
        storage: StorageClient,
    ):
        self.doc_repo = DocumentRepository(session)
        self.session = session
        self.gemini = gemini
        self.chroma = chroma
        self.storage = storage

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """Split text into overlapping chunks for embedding."""
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    async def upload(
        self, user_id: UUID, org_id: UUID, filename: str, content: bytes
    ) -> Document:
        """Upload, parse, embed, and store a legal document."""
        settings = get_settings()

        # Validate file type
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise BadRequestException(
                f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Validate file size
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise BadRequestException(
                f"File is too large ({len(content)} bytes). Maximum: {settings.MAX_FILE_SIZE_MB}MB"
            )

        # Determine file_type from extension
        file_type = ext.lstrip('.')

        # Create initial document record
        doc = await self.doc_repo.create(
            user_id=user_id,
            org_id=org_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(content),
            storage_key="",  # Will be updated after upload
            status=DocumentStatus.UPLOADED.value,
        )

        try:
            # Upload original to storage
            storage_key = self.storage.upload_file(
                str(org_id), str(doc.id), filename, content
            )

            # Parse file to extract raw text
            raw_text = parse_file(filename, content)

            # Update status to processing
            doc = await self.doc_repo.update_status(doc.id, DocumentStatus.PROCESSING.value)

            # Chunk the text
            chunks = self._chunk_text(raw_text)

            # Embed chunks via Gemini
            embeddings: list[list[float]] = []
            for chunk in chunks:
                emb = await asyncio.to_thread(self.gemini.embed_text, chunk)
                embeddings.append(emb)

            # Store in ChromaDB (per-org collection)
            self.chroma.add_documents(str(org_id), str(doc.id), chunks, embeddings)

            # Update document to analyzed
            doc.storage_key = storage_key
            doc.status = DocumentStatus.ANALYZED.value
            doc.chunk_count = len(chunks)
            doc.raw_text_preview = raw_text[:500]
            await self.session.flush()
            await self.session.refresh(doc)

            logger.info(
                "document_uploaded",
                doc_id=str(doc.id),
                chunks=len(chunks),
                file_type=file_type,
            )
            return doc

        except Exception as e:
            logger.error("document_upload_failed", doc_id=str(doc.id), error=str(e))
            doc.status = DocumentStatus.FAILED.value
            await self.session.flush()
            raise

    async def list_documents(
        self, org_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[Document], int]:
        """List documents for an organization (paginated)."""
        offset = (page - 1) * page_size
        return await self.doc_repo.list_by_org(org_id, offset=offset, limit=page_size)

    async def get_document(self, doc_id: UUID, org_id: UUID) -> Document:
        """Get a single document, scoped to the user's org."""
        doc = await self.doc_repo.get_by_id(doc_id)
        if not doc or doc.org_id != org_id or doc.is_deleted:
            raise NotFoundException("Document not found")
        return doc

    async def delete_document(
        self, doc_id: UUID, org_id: UUID, user_id: UUID, user_role: str
    ) -> Document:
        """Soft-delete a document. Admins can delete any doc; others only their own."""
        doc = await self.get_document(doc_id, org_id)

        if user_role != UserRole.ADMIN.value and doc.user_id != user_id:
            raise ForbiddenException("You do not have permission to delete this document")

        # Clean up vector store
        self.chroma.delete_document(str(org_id), str(doc_id))

        return await self.doc_repo.soft_delete(doc_id)
