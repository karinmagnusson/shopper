import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pinterest_id: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String, index=True)
    access_token: Mapped[str | None] = mapped_column(String)
    refresh_token: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    style_preferences: Mapped[dict | None] = mapped_column(JSONB)
