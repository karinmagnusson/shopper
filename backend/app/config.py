"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application environment settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/shopper"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Pinterest OAuth
    PINTEREST_CLIENT_ID: str = ""
    PINTEREST_CLIENT_SECRET: str = ""
    PINTEREST_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # JWT
    JWT_SECRET: str = "change-me-in-production-use-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Google Vision
    GOOGLE_VISION_API_KEY: str = ""

    # Amazon Associates
    AMAZON_ASSOCIATE_TAG: str = ""
    AMAZON_ACCESS_KEY: str = ""
    AMAZON_SECRET_KEY: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # App
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
