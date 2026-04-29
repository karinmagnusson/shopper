import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str | None = None
    style_preferences: dict | None = None


class UserCreate(UserBase):
    pinterest_id: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pinterest_id: str | None
    created_at: datetime
    last_sync: datetime | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
