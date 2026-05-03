"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Pinterest API
    pinterest_app_id: str
    pinterest_app_secret: str
    pinterest_redirect_uri: str = "http://localhost:8000/auth/pinterest/callback"
    
    # Amazon Product Advertising API
    amazon_access_key: str
    amazon_secret_key: str
    amazon_associate_tag: str
    amazon_region: str = "US"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Database
    database_url: str = "sqlite:///./shopper.db"
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
