from uuid import UUID
from fastapi import APIRouter, Depends, Query as QueryParam
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
from app.schemas.auth import UserResponse
from app.schemas.common import PaginatedResponse
from app.repositories.user_repo import UserRepository
from app.middleware.auth import require_roles
from app.models import User
from app.core.constants import UserRole
from app.core.exceptions import BadRequestException, NotFoundException

router = APIRouter(prefix='/admin', tags=['Admin'])

@router.get('/users', response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = QueryParam(default=1, ge=1),
    page_size: int = QueryParam(default=20, ge=1, le=100),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session)
    users, total = await user_repo.get_by_org(
        org_id=current_user.org_id,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    total_pages = (total + page_size - 1) // page_size
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@router.patch('/users/{user_id}/role', response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    role: str,  # Accept as query param or body
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    session: AsyncSession = Depends(get_session),
):
    if role not in [r.value for r in UserRole]:
        raise BadRequestException(f'Invalid role. Must be one of: {[r.value for r in UserRole]}')
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user or user.org_id != current_user.org_id:
        raise NotFoundException('User not found')
    
    updated_user = await user_repo.update(user_id, role=role)
    return updated_user
