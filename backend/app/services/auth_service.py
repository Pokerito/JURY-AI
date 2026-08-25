"""Authentication service — registration, login, and token refresh."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.organization import Organization
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse
from app.core.exceptions import ConflictException, UnauthorizedException, ForbiddenException
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.constants import UserRole
from app.config import get_settings


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.session = session

    async def register(self, email: str, password: str, full_name: str, org_name: str) -> tuple[User, TokenResponse]:
        """Register a new user and organization."""
        # Check if email exists
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ConflictException("User with this email already exists")

        # Create Organization
        org_slug = org_name.lower().replace(" ", "-").replace("_", "-")
        org = Organization(name=org_name, slug=org_slug)
        self.session.add(org)
        await self.session.flush()

        # Create User (first user in org is always ADMIN)
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            org_id=org.id,
            role=UserRole.ADMIN.value,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        # Generate tokens
        settings = get_settings()
        token_data = {"sub": str(user.id), "org_id": str(user.org_id), "role": user.role}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return user, token_response

    async def login(self, email: str, password: str) -> tuple[User, TokenResponse]:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("Account is inactive")

        await self.user_repo.update_last_login(user.id)

        settings = get_settings()
        token_data = {"sub": str(user.id), "org_id": str(user.org_id), "role": user.role}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return user, token_response

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue new token pair."""
        payload = decode_token(refresh_token)
        if payload.get("token_type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        role = payload.get("role")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        settings = get_settings()
        token_data = {"sub": user_id, "org_id": org_id, "role": role}
        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
