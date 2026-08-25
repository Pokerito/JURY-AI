class JuryAIException(Exception):
    """Base exception for Jury-AI application."""
    def __init__(self, detail: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)

class NotFoundException(JuryAIException):
    """Resource not found exception."""
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(detail=detail, status_code=404, error_code=error_code)

class UnauthorizedException(JuryAIException):
    """Unauthorized access exception."""
    def __init__(self, detail: str = "Unauthorized", error_code: str = "UNAUTHORIZED"):
        super().__init__(detail=detail, status_code=401, error_code=error_code)

class ForbiddenException(JuryAIException):
    """Forbidden action exception."""
    def __init__(self, detail: str = "Forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(detail=detail, status_code=403, error_code=error_code)

class BadRequestException(JuryAIException):
    """Bad request exception."""
    def __init__(self, detail: str = "Bad Request", error_code: str = "BAD_REQUEST"):
        super().__init__(detail=detail, status_code=400, error_code=error_code)

class ConflictException(JuryAIException):
    """Resource conflict exception."""
    def __init__(self, detail: str = "Conflict", error_code: str = "CONFLICT"):
        super().__init__(detail=detail, status_code=409, error_code=error_code)

class RateLimitException(JuryAIException):
    """Rate limit exceeded exception."""
    def __init__(self, detail: str = "Rate Limit Exceeded", error_code: str = "RATE_LIMIT"):
        super().__init__(detail=detail, status_code=429, error_code=error_code)

class ExternalServiceException(JuryAIException):
    """External service failure exception."""
    def __init__(self, detail: str = "External Service Error", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(detail=detail, status_code=502, error_code=error_code)
