"""Pydantic schemas for User."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Data required to create a user (populated from Pinterest OAuth)."""

    pinterest_id: str
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    """Fields a user may update directly."""

    email: EmailStr | None = None
    display_name: str | None = None
    style_preferences: dict | None = None


class UserResponse(BaseModel):
    """Public representation of a User."""

    model_config = {"from_attributes": True}

    id: UUID
    pinterest_id: str
    email: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    last_sync: datetime | None = None
    is_active: bool


class UserProfile(UserResponse):
    """Extended profile including preferences."""

    style_preferences: dict = {}
