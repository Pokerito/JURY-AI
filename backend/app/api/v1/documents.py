from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, Request, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session, get_gemini_client, get_chroma_manager, get_storage_client
from app.schemas.documents import DocumentResponse
from app.schemas.common import PaginatedResponse
from app.services.document_service import DocumentService
from app.middleware.auth import get_current_user
from app.models import User
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException

router = APIRouter(prefix='/documents', tags=['Documents'])

@router.post('/upload', response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Check role: must be analyst or admin
    if current_user.role == UserRole.VIEWER.value:
        raise ForbiddenException('Viewers cannot upload documents')
    
    content = await file.read()
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    document = await doc_service.upload(
        user_id=current_user.id,
        org_id=current_user.org_id,
        filename=file.filename,
        content=content,
    )
    return document

@router.get('', response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    page: int = QueryParam(default=1, ge=1),
    page_size: int = QueryParam(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    documents, total = await doc_service.list_documents(
        org_id=current_user.org_id,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size
    return PaginatedResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.get('/{doc_id}', response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    document = await doc_service.get_document(doc_id=doc_id, org_id=current_user.org_id)
    return document

@router.delete('/{doc_id}', status_code=204)
async def delete_document(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    await doc_service.delete_document(
        doc_id=doc_id,
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_role=current_user.role,
    )
