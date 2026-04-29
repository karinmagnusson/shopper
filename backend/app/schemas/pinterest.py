import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pinterest_board_id: str
    name: str
    description: str | None
    cover_image_url: str | None
    pin_count: int
    last_synced: datetime | None


class PinRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pinterest_pin_id: str
    image_url: str | None
    description: str | None
    link: str | None
    analyzed_at: datetime | None
    analysis_data: dict | None


class AnalysisResult(BaseModel):
    pin_id: str
    colors: list[str]
    clothing_types: list[str]
    styles: list[str]
    confidence: float
