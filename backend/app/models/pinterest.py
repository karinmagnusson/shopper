"""SQLAlchemy Pinterest board and pin models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PinterestBoard(Base):
    """Cached Pinterest board metadata."""

    __tablename__ = "pinterest_boards"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(native_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pinterest_board_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String, nullable=True)
    pin_count = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    synced_at = Column(DateTime, nullable=True)
    board_metadata = Column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="boards")
    pins = relationship("PinterestPin", back_populates="board", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<PinterestBoard id={self.id} name={self.name}>"


class PinterestPin(Base):
    """Cached Pinterest pin with fashion analysis results."""

    __tablename__ = "pinterest_pins"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    board_id = Column(UUID(native_uuid=True), ForeignKey("pinterest_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    pinterest_pin_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    saved_at = Column(DateTime, nullable=True)
    # Fashion analysis results stored as JSON
    analysis_data = Column(JSON, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)

    board = relationship("PinterestBoard", back_populates="pins")

    def __repr__(self) -> str:
        return f"<PinterestPin id={self.id} pinterest_pin_id={self.pinterest_pin_id}>"
