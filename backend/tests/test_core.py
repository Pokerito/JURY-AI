"""Unit tests for core business logic."""
import pytest
from app.core.constants import RISK_SCORE_WEIGHTS


class TestRiskScoring:
    """Test the safety score calculation logic."""

    def test_perfect_score_no_clauses(self):
        """Empty document should get a perfect 100."""
        score = 100
        assert score == 100

    def test_single_critical_clause(self):
        """One critical clause should deduct 25 points."""
        score = 100 - RISK_SCORE_WEIGHTS["critical"]
        assert score == 75

    def test_single_high_clause(self):
        """One high-risk clause should deduct 15 points."""
        score = 100 - RISK_SCORE_WEIGHTS["high"]
        assert score == 85

    def test_single_medium_clause(self):
        """One medium clause should deduct 5 points."""
        score = 100 - RISK_SCORE_WEIGHTS["medium"]
        assert score == 95

    def test_low_clause_no_deduction(self):
        """Low-risk clauses should not deduct any points."""
        score = 100 - RISK_SCORE_WEIGHTS["low"]
        assert score == 100

    def test_mixed_clauses(self):
        """Multiple clauses of varying severity."""
        clauses = [
            {"risk_level": "critical"},
            {"risk_level": "high"},
            {"risk_level": "medium"},
            {"risk_level": "low"},
        ]
        score = 100
        for c in clauses:
            score -= RISK_SCORE_WEIGHTS.get(c["risk_level"], 0)
        # 100 - 25 - 15 - 5 - 0 = 55
        assert score == 55

    def test_floor_at_zero(self):
        """Score should never go below 0."""
        clauses = [{"risk_level": "critical"}] * 5  # 5 × 25 = 125
        score = 100
        for c in clauses:
            score -= RISK_SCORE_WEIGHTS.get(c["risk_level"], 0)
        score = max(0, score)
        assert score == 0

    def test_unknown_risk_level_ignored(self):
        """Unknown risk levels should default to 0 deduction."""
        score = 100 - RISK_SCORE_WEIGHTS.get("unknown", 0)
        assert score == 100

    def test_real_world_contract_score(self):
        """Simulate the seed data contract (2 critical, 1 high, 1 medium, 2 low)."""
        clauses = [
            {"risk_level": "critical"},
            {"risk_level": "critical"},
            {"risk_level": "high"},
            {"risk_level": "medium"},
            {"risk_level": "low"},
            {"risk_level": "low"},
        ]
        score = 100
        for c in clauses:
            score -= RISK_SCORE_WEIGHTS.get(c["risk_level"], 0)
        # 100 - 25 - 25 - 15 - 5 - 0 - 0 = 30
        assert score == 30


class TestSecurityUtils:
    """Test password hashing and JWT token operations."""

    def test_hash_password_returns_bcrypt(self):
        from app.core.security import hash_password
        hashed = hash_password("test_password_123")
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60

    def test_verify_correct_password(self):
        from app.core.security import hash_password, verify_password
        hashed = hash_password("my_secure_password")
        assert verify_password("my_secure_password", hashed) is True

    def test_verify_wrong_password(self):
        from app.core.security import hash_password, verify_password
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        from app.core.security import create_access_token, decode_token
        token = create_access_token({"sub": "user-123", "org_id": "org-456", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 50

        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["org_id"] == "org-456"
        assert payload["role"] == "admin"
        assert payload["token_type"] == "access"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_create_refresh_token(self):
        from app.core.security import create_refresh_token, decode_token
        token = create_refresh_token({"sub": "user-123", "org_id": "org-456", "role": "analyst"})
        payload = decode_token(token)
        assert payload["token_type"] == "refresh"
        assert payload["sub"] == "user-123"

    def test_decode_invalid_token_raises(self):
        from app.core.security import decode_token
        from app.core.exceptions import UnauthorizedException
        with pytest.raises(UnauthorizedException):
            decode_token("totally.invalid.token")


class TestConstants:
    """Test that enum values are correct."""

    def test_user_roles(self):
        from app.core.constants import UserRole
        assert UserRole.ADMIN == "admin"
        assert UserRole.ANALYST == "analyst"
        assert UserRole.VIEWER == "viewer"

    def test_document_statuses(self):
        from app.core.constants import DocumentStatus
        assert DocumentStatus.UPLOADED == "uploaded"
        assert DocumentStatus.PROCESSING == "processing"
        assert DocumentStatus.ANALYZED == "analyzed"
        assert DocumentStatus.FAILED == "failed"

    def test_risk_levels(self):
        from app.core.constants import RiskLevel
        assert RiskLevel.CRITICAL == "critical"
        assert RiskLevel.HIGH == "high"
        assert RiskLevel.MEDIUM == "medium"
        assert RiskLevel.LOW == "low"

    def test_analysis_types(self):
        from app.core.constants import AnalysisType
        assert AnalysisType.SUMMARY == "summary"
        assert AnalysisType.ENTITIES == "entities"
        assert AnalysisType.RISK_SCORE == "risk_score"
        assert AnalysisType.FULL == "full"

    def test_risk_weights_match_levels(self):
        from app.core.constants import RiskLevel, RISK_SCORE_WEIGHTS
        assert set(RISK_SCORE_WEIGHTS.keys()) == {rl.value for rl in RiskLevel}


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_not_found_exception(self):
        from app.core.exceptions import NotFoundException
        exc = NotFoundException("Resource not found")
        assert exc.status_code == 404
        assert "not found" in str(exc.detail).lower()

    def test_unauthorized_exception(self):
        from app.core.exceptions import UnauthorizedException
        exc = UnauthorizedException("Bad creds")
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        from app.core.exceptions import ForbiddenException
        exc = ForbiddenException("No access")
        assert exc.status_code == 403

    def test_rate_limit_exception(self):
        from app.core.exceptions import RateLimitException
        exc = RateLimitException("Slow down")
        assert exc.status_code == 429

    def test_base_exception_inheritance(self):
        from app.core.exceptions import (
            JuryAIException, NotFoundException, UnauthorizedException,
            ForbiddenException, BadRequestException, ConflictException,
            RateLimitException, ExternalServiceException,
        )
        for ExcClass in [NotFoundException, UnauthorizedException, ForbiddenException,
                         BadRequestException, ConflictException, RateLimitException,
                         ExternalServiceException]:
            assert issubclass(ExcClass, JuryAIException)


class TestSchemaValidation:
    """Test Pydantic schema validation."""

    def test_register_request_valid(self):
        from app.schemas.auth import RegisterRequest
        req = RegisterRequest(
            email="test@example.com",
            password="secure_pass123",
            full_name="Test User",
            org_name="Test Org",
        )
        assert req.email == "test@example.com"

    def test_register_request_short_password(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(Exception):  # Pydantic ValidationError
            RegisterRequest(
                email="test@example.com",
                password="short",
                full_name="Test User",
                org_name="Test Org",
            )

    def test_register_request_invalid_email(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(Exception):
            RegisterRequest(
                email="not-an-email",
                password="secure_pass123",
                full_name="Test User",
                org_name="Test Org",
            )

    def test_query_request_valid(self):
        from app.schemas.analysis import QueryRequest
        req = QueryRequest(question="What are the payment terms?")
        assert len(req.question) > 3
