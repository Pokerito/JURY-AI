import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import JuryAIException

logger = structlog.get_logger()

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(JuryAIException)
    async def jury_ai_exception_handler(request: Request, exc: JuryAIException):
        logger.error("jury_ai_exception", error=str(exc), status_code=exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "detail": exc.detail, "error_code": getattr(exc, 'error_code', None)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error("validation_exception", errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "details": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "details": None
            }
        )
