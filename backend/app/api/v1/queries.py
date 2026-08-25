from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session, get_gemini_client, get_chroma_manager, get_storage_client
from app.schemas.analysis import QueryRequest, QueryResponse
from app.services.document_service import DocumentService
from app.services.rag_service import RAGQueryService
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter(prefix='/documents/{doc_id}', tags=['RAG Q&A'])

@router.post('/query', response_model=QueryResponse)
async def query_document(
    doc_id: UUID,
    body: QueryRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Verify document belongs to org
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    await doc_service.get_document(doc_id=doc_id, org_id=current_user.org_id)
    
    rag_service = RAGQueryService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
    )
    query_record = await rag_service.query(
        doc_id=doc_id,
        org_id=current_user.org_id,
        user_id=current_user.id,
        question=body.question,
    )
    return query_record
