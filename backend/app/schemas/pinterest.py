"""Pydantic schemas for Pinterest boards and pins."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BoardResponse(BaseModel):
    """Serialised Pinterest board."""

    model_config = {"from_attributes": True}

    id: UUID
    pinterest_board_id: str
    name: str
    description: str | None = None
    cover_image_url: str | None = None
    pin_count: int = 0
    follower_count: int = 0
    synced_at: datetime | None = None


class PinResponse(BaseModel):
    """Serialised Pinterest pin."""

    model_config = {"from_attributes": True}

    id: UUID
    pinterest_pin_id: str
    title: str | None = None
    description: str | None = None
    image_url: str
    link: str | None = None
    analysis_data: dict | None = None
    analyzed_at: datetime | None = None


class SyncRequest(BaseModel):
    """Request body to trigger a board sync."""

    board_ids: list[str] | None = None  # None means sync all boards


class AnalyzeRequest(BaseModel):
    """Request body to run fashion analysis on selected pins."""

    pin_ids: list[str]
