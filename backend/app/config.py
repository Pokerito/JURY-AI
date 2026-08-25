from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets

class Settings(BaseSettings):
    """Application settings using pydantic-settings."""
    APP_NAME: str = 'Jury-AI'
    APP_VERSION: str = '1.0.0'
    DEBUG: bool = False
    API_V1_PREFIX: str = '/api/v1'
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/jury_ai'
    REDIS_URL: str = 'redis://localhost:6379/0'
    GOOGLE_API_KEY: str = ''
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_FILE_SIZE_MB: int = 10
    CHROMA_PERSIST_DIR: str = './data/chroma'
    S3_BUCKET_NAME: str = 'jury-ai-documents'
    S3_REGION: str = 'ap-south-1'
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_DIR: str = './data/uploads'
    CORS_ORIGINS: list[str] = ['http://localhost:3000']
    RATE_LIMIT_PER_MINUTE: int = 100

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    """Returns the application settings."""
    return Settings()
