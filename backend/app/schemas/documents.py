import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.common import PaginatedResponse

class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    raw_text_preview: str | None = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(PaginatedResponse[DocumentResponse]):
    pass
