import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class RiskClauseResponse(BaseModel):
    clause_name: str
    risk_level: str
    justification: str
    safer_alternative: str | None = None
    sort_order: int

    model_config = ConfigDict(from_attributes=True)

class AnalysisResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    analysis_type: str
    result: dict | None = None
    safety_score: int | None = None
    processing_time_ms: int | None = None
    model_used: str | None = None
    risk_clauses: list[RiskClauseResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RiskScoreResponse(BaseModel):
    score: int
    checklist: list[RiskClauseResponse]
    all_clauses: list[RiskClauseResponse]

class QueryRequest(BaseModel):
    question: str = Field(min_length=3)

class QueryResponse(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    processing_time_ms: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EntityResponse(BaseModel):
    parties: list[str]
    dates: list[str]
    amounts: list[str]
    jurisdictions: list[str]

class SummaryResponse(BaseModel):
    summary: str
    document_id: uuid.UUID

class AnalyzeTriggerResponse(BaseModel):
    message: str
    analysis_id: uuid.UUID
    document_id: uuid.UUID
