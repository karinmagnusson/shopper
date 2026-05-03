from __future__ import annotations

import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "sqlite:///./shopper.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-at-least-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Pinterest OAuth
    PINTEREST_APP_ID: str = ""
    PINTEREST_APP_SECRET: str = ""
    PINTEREST_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # Google Vision API
    GOOGLE_VISION_API_KEY: str = ""

    # Amazon Associates
    AMAZON_ASSOCIATE_TAG: str = ""
    AMAZON_ACCESS_KEY: str = ""
    AMAZON_SECRET_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://*.railway.app", "https://*.up.railway.app"]

    # App
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return [o.strip() for o in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def pinterest_oauth_url(self) -> str:
        return "https://www.pinterest.com/oauth/"

    @property
    def pinterest_api_base(self) -> str:
        return "https://api.pinterest.com/v5"


settings = Settings()
