import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PinterestBoard(Base):
    __tablename__ = "pinterest_boards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    pinterest_board_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String)
    pin_count: Mapped[int] = mapped_column(Integer, default=0)
    last_synced: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pins: Mapped[list["PinterestPin"]] = relationship(
        "PinterestPin", back_populates="board", cascade="all, delete-orphan"
    )


class PinterestPin(Base):
    __tablename__ = "pinterest_pins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pinterest_boards.id", ondelete="CASCADE"), index=True
    )
    pinterest_pin_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    image_url: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    analysis_data: Mapped[dict | None] = mapped_column(JSONB)

    board: Mapped["PinterestBoard"] = relationship("PinterestBoard", back_populates="pins")
