"""Dependency injection — database sessions and service singletons."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import get_settings
from app.integrations.gemini_client import GeminiClient
from app.integrations.chroma_client import ChromaManager
from app.integrations.s3_client import StorageClient
from app.integrations.redis_client import RedisManager

# ── Module-level singletons ──────────────────────────────────────────────────
_engine = None
_session_factory = None


async def init_db() -> None:
    """Initialize the async database engine and session factory."""
    global _engine, _session_factory
    settings = get_settings()
    if "sqlite" in settings.DATABASE_URL:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
        )
        # Auto-create tables for SQLite local dev
        from app.models.base import Base
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=20,
            max_overflow=10,
            echo=settings.DEBUG,
        )
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )


async def close_db() -> None:
    """Dispose of the database engine connection pool."""
    global _engine
    if _engine:
        await _engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session with auto-commit/rollback."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_gemini_client() -> GeminiClient:
    """Return the singleton GeminiClient instance."""
    return GeminiClient()  # Singleton via __new__


def get_chroma_manager() -> ChromaManager:
    """Return the singleton ChromaManager instance."""
    return ChromaManager()  # Singleton via __new__


def get_storage_client() -> StorageClient:
    """Return the singleton StorageClient instance."""
    return StorageClient()  # Singleton via __new__


def get_redis_manager() -> RedisManager:
    """Return the singleton RedisManager instance."""
    return RedisManager()  # Singleton via __new__
