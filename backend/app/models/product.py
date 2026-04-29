import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    retailer_id: Mapped[str | None] = mapped_column(String)
    retailer_name: Mapped[str | None] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String)
    product_url: Mapped[str | None] = mapped_column(String)
    affiliate_url: Mapped[str | None] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String, index=True)
    brand: Mapped[str | None] = mapped_column(String, index=True)
    colors: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    sizes: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    style_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    interaction_type: Mapped[str] = mapped_column(String)  # view, click, save, purchase
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
