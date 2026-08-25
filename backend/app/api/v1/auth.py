from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register', response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService(session)
    user, tokens = await auth_service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        org_name=body.org_name,
    )
    return tokens

@router.post('/login', response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService(session)
    user, tokens = await auth_service.login(email=body.email, password=body.password)
    return tokens

@router.post('/refresh', response_model=TokenResponse)
async def refresh(body: RefreshRequest, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService(session)
    tokens = await auth_service.refresh_token(body.refresh_token)
    return tokens

@router.get('/me', response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
