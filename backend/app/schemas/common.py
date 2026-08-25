from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    error_code: str | None = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    checks: dict[str, str]
