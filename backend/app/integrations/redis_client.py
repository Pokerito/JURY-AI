import redis.asyncio as redis
import structlog
from app.config import get_settings

logger = structlog.get_logger(__name__)

class RedisManager:
    """Singleton manager for Redis connections with in-memory fallback for local dev."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)
            cls._instance.redis_client = None
        return cls._instance

    def init_redis(self, url: str | None = None):
        """Initialize the Redis connection pool with in-memory fallback."""
        if url is None:
            url = get_settings().REDIS_URL
        try:
            self.redis_client = redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        except Exception as e:
            logger.warning("redis_connection_fallback", error=str(e))
            try:
                import fakeredis.aioredis
                self.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
            except Exception:
                self.redis_client = None

    def get_redis(self):
        """Get the active Redis connection instance."""
        if self.redis_client is None:
            try:
                import fakeredis.aioredis
                self.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
            except Exception:
                self.init_redis()
        return self.redis_client
        
    async def close_redis(self):
        """Close the active Redis connection gracefully."""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception:
                pass

redis_manager = RedisManager()
