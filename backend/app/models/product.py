"""SQLAlchemy Product model."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    """Represents an affiliate product with fashion metadata."""

    __tablename__ = "products"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    asin = Column(String, unique=True, index=True, nullable=True)  # Amazon ASIN
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    brand = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True, index=True)
    price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    image_url = Column(String, nullable=True)
    affiliate_url = Column(String, nullable=False)
    # Stored as JSON arrays for cross-database compatibility (PostgreSQL / SQLite)
    colors = Column(JSON, default=list, nullable=False)
    sizes = Column(JSON, default=list, nullable=False)
    style_tags = Column(JSON, default=list, nullable=False)
    rating = Column(Numeric(3, 2), nullable=True)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recommendations = relationship("ProductRecommendation", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("UserInteraction", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_category_brand", "category", "brand"),
        Index("ix_products_price", "price"),
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} title={self.title}>"
