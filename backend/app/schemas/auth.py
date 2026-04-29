"""Pydantic schemas for authentication."""

from pydantic import BaseModel


class OAuthCallbackRequest(BaseModel):
    """Pinterest OAuth callback payload from frontend."""

    code: str
    state: str | None = None


class TokenResponse(BaseModel):
    """JWT token payload returned to client."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginResponse(BaseModel):
    """Full login response including token and basic user info."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    display_name: str | None = None
    avatar_url: str | None = None
