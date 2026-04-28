from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = Field(description="PostgreSQL async connection URL")
    REDIS_URL: str = Field(description="Redis connection URL")

    PINTEREST_CLIENT_ID: str = Field(description="Pinterest OAuth app client ID")
    PINTEREST_CLIENT_SECRET: str = Field(description="Pinterest OAuth app client secret")
    PINTEREST_REDIRECT_URI: str = Field(description="OAuth callback URI registered with Pinterest")

    GOOGLE_VISION_API_KEY: str = Field(description="Google Cloud Vision API key")

    AMAZON_ACCESS_KEY: str = Field(description="Amazon Product Advertising API access key")
    AMAZON_SECRET_KEY: str = Field(description="Amazon Product Advertising API secret key")
    AMAZON_ASSOCIATE_TAG: str = Field(description="Amazon Associates tracking tag")

    JWT_SECRET_KEY: str = Field(description="Secret key for signing JWT tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT expiry in minutes")

    RATE_LIMIT_REQUESTS: int = Field(default=1000, description="Max requests per rate limit window")
    RATE_LIMIT_WINDOW: int = Field(default=3600, description="Rate limit window in seconds")

    TOKEN_ENCRYPTION_KEY: str = Field(description="Fernet key for encrypting Pinterest access tokens")

    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )


settings = Settings()
