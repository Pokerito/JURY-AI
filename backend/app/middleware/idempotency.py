import json
from fastapi import Request
from app.integrations.redis_client import RedisManager

async def check_idempotency(request: Request) -> str | dict | None:
    """
    Check if the request has an idempotency key and return cached response if it exists.
    Returns the key if fresh, dict if cached, or None if no key.
    """
    key = request.headers.get('X-Idempotency-Key')
    if not key:
        return None
        
    redis = await RedisManager.get_redis()
    cached = await redis.get(f'idem:{key}')
    if cached:
        return json.loads(cached)  # Return cached response
        
    return key  # Key is fresh, proceed with processing

async def save_idempotency(key: str, response_data: dict, ttl: int = 86400):
    """
    Save the response data for an idempotency key.
    """
    redis = await RedisManager.get_redis()
    await redis.setex(f'idem:{key}', ttl, json.dumps(response_data, default=str))
