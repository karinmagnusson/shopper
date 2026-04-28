import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PinterestBoard(Base):
    __tablename__ = "pinterest_boards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pinterest_board_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pin_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_synced: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    pins: Mapped[list["PinterestPin"]] = relationship(
        "PinterestPin", back_populates="board", cascade="all, delete-orphan"
    )


class PinterestPin(Base):
    __tablename__ = "pinterest_pins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pinterest_boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pinterest_pin_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    analyzed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    board: Mapped["PinterestBoard"] = relationship("PinterestBoard", back_populates="pins")
