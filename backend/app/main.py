"""FastAPI application factory — creates and configures the Jury-AI API."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import get_settings
from app.api.v1.router import api_v1_router
from app.dependencies import init_db, close_db, get_redis_manager, get_chroma_manager
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logging import RequestLoggingMiddleware, configure_logging
from app.schemas.common import HealthResponse

_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    configure_logging()
    settings = get_settings()

    # Initialize database
    await init_db()

    # Initialize Redis
    try:
        redis_mgr = get_redis_manager()
        redis_mgr.init_redis(settings.REDIS_URL)
    except Exception:
        pass

    yield

    # Shutdown
    try:
        redis_mgr = get_redis_manager()
        await redis_mgr.close_redis()
    except Exception:
        pass
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Jury-AI API",
        description="AI-Powered Legal Document Intelligence Platform",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    register_exception_handlers(app)

    # ── Health check (public, outside versioned API) ─────────────────────
    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        checks: dict[str, str] = {}

        # Database check
        try:
            from app.dependencies import _engine

            async with _engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "disconnected"

        # Redis check
        try:
            redis_mgr = get_redis_manager()
            redis = redis_mgr.get_redis()
            await redis.ping()
            checks["redis"] = "connected"
        except Exception:
            checks["redis"] = "disconnected"

        # ChromaDB check
        try:
            get_chroma_manager()
            checks["chromadb"] = "connected"
        except Exception:
            checks["chromadb"] = "disconnected"

        # Gemini API check
        checks["gemini_api"] = (
            "configured" if settings.GOOGLE_API_KEY else "not_configured"
        )

        overall = (
            "healthy"
            if all(v in ("connected", "configured") for v in checks.values())
            else "degraded"
        )

        return HealthResponse(
            status=overall,
            version=settings.APP_VERSION,
            uptime_seconds=round(time.time() - _start_time, 2),
            checks=checks,
        )

    # Include versioned API router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
