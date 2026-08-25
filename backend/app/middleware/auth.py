"""JWT authentication middleware — FastAPI dependencies for auth and RBAC."""
import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.constants import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.dependencies import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Extract and validate the current user from the JWT bearer token."""
    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("token_type") != "access":
        raise UnauthorizedException("Invalid token type — expected access token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user id in token")

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ForbiddenException("Account is inactive")

    return user


def require_roles(*roles: UserRole):
    """Dependency factory that checks if the current user has one of the required roles."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_values = [r.value for r in roles]
        if current_user.role not in role_values:
            raise ForbiddenException("Insufficient permissions")
        return current_user

    return role_checker
