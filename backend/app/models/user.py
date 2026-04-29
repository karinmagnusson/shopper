"""SQLAlchemy User model."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """Represents an authenticated Pinterest user."""

    __tablename__ = "users"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    pinterest_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_sync = Column(DateTime, nullable=True)
    style_preferences = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    boards = relationship("PinterestBoard", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("ProductRecommendation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} pinterest_id={self.pinterest_id}>"
