from enum import StrEnum

class UserRole(StrEnum):
    ADMIN = 'admin'
    ANALYST = 'analyst'
    VIEWER = 'viewer'

class DocumentStatus(StrEnum):
    UPLOADED = 'uploaded'
    PROCESSING = 'processing'
    ANALYZED = 'analyzed'
    FAILED = 'failed'

class RiskLevel(StrEnum):
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class AnalysisType(StrEnum):
    SUMMARY = 'summary'
    ENTITIES = 'entities'
    RISK_SCORE = 'risk_score'
    FULL = 'full'

RISK_SCORE_WEIGHTS: dict[str, int] = {
    RiskLevel.CRITICAL: 25,
    RiskLevel.HIGH: 15,
    RiskLevel.MEDIUM: 5,
    RiskLevel.LOW: 0
}
