from fastapi import Depends, Request
from app.models.user import User
from app.middleware.auth import get_current_user
from app.integrations.redis_client import RedisManager
from app.config import get_settings
from app.core.exceptions import JuryAIException

class RateLimitException(JuryAIException):
    def __init__(self, message: str = "Rate limit exceeded. Try again later."):
        super().__init__(status_code=429, message=message)

async def rate_limit_dependency(request: Request, current_user: User = Depends(get_current_user)):
    redis = await RedisManager.get_redis()
    key = f"rate:{current_user.id}:{request.url.path}"
    
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, 60)  # 60 second window
        
    settings = get_settings()
    # Assuming settings has RATE_LIMIT_PER_MINUTE
    limit = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 100) 
    
    if current > limit:
        raise RateLimitException()
