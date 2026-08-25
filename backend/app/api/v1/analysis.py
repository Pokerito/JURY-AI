import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session, get_gemini_client, get_chroma_manager, get_storage_client
from app.schemas.analysis import AnalyzeTriggerResponse, SummaryResponse, EntityResponse, RiskScoreResponse
from app.services.document_service import DocumentService
from app.services.risk_service import RiskAnalysisService
from app.services.entity_service import EntityExtractionService
from app.middleware.auth import get_current_user
from app.middleware.idempotency import save_idempotency
from app.models import User
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException, NotFoundException

router = APIRouter(prefix='/documents/{doc_id}', tags=['Analysis'])

@router.post('/analyze', response_model=AnalyzeTriggerResponse, status_code=201)
async def trigger_analysis(
    doc_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if current_user.role == UserRole.VIEWER.value:
        raise ForbiddenException('Viewers cannot trigger analysis')
    
    idempotency_key = request.headers.get('X-Idempotency-Key')
    
    risk_service = RiskAnalysisService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
    )
    analysis = await risk_service.analyze_risk(
        doc_id=doc_id,
        org_id=current_user.org_id,
        idempotency_key=idempotency_key,
    )
    
    # Cache the response for idempotency
    if idempotency_key:
        response_data = {
            'message': 'Analysis completed successfully',
            'analysis_id': str(analysis.id),
            'document_id': str(doc_id),
        }
        await save_idempotency(idempotency_key, response_data)
    
    return AnalyzeTriggerResponse(
        message='Analysis completed successfully',
        analysis_id=analysis.id,
        document_id=doc_id,
    )

@router.get('/summary', response_model=SummaryResponse)
async def get_summary(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # First verify doc belongs to user's org
    doc_service = DocumentService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
        storage=get_storage_client(),
    )
    doc = await doc_service.get_document(doc_id=doc_id, org_id=current_user.org_id)
    
    chroma = get_chroma_manager()
    gemini = get_gemini_client()
    
    full_text = chroma.get_full_text(str(current_user.org_id), str(doc_id), cap=8000)
    if not full_text:
        if doc and doc.raw_text_preview:
            full_text = doc.raw_text_preview
        else:
            raise NotFoundException('Document content not found')
    
    prompt = f"""You are a legal document analyst. Write a concise 2-3 sentence plain-English summary of this legal document.
Mention: what type of agreement it is, who the parties are (if mentioned), and the key subject matter.
Be direct and factual. No bullet points.

Document:
{full_text}

Summary:"""
    summary_text = await asyncio.to_thread(gemini.generate_content, prompt)
    return SummaryResponse(summary=summary_text.strip(), document_id=doc_id)

@router.get('/entities', response_model=EntityResponse)
async def get_entities(
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
    await doc_service.get_document(doc_id=doc_id, org_id=current_user.org_id)
    
    entity_service = EntityExtractionService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
    )
    entities = await entity_service.extract_entities(
        doc_id=doc_id,
        org_id=current_user.org_id,
    )
    return EntityResponse(**entities)

@router.get('/risk-score', response_model=RiskScoreResponse)
async def get_risk_score(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    risk_service = RiskAnalysisService(
        session=session,
        gemini=get_gemini_client(),
        chroma=get_chroma_manager(),
    )
    result = await risk_service.get_risk_score(
        doc_id=doc_id,
        org_id=current_user.org_id,
    )
    return result
