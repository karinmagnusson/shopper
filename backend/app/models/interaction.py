"""SQLAlchemy UserInteraction and ProductRecommendation models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserInteraction(Base):
    """Tracks user clicks and interactions with products."""

    __tablename__ = "user_interactions"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(native_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(native_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String, nullable=False)  # "click", "save", "purchase"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_id = Column(String, nullable=True)
    referrer_pin_id = Column(String, nullable=True)  # Pinterest pin that drove the click

    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<UserInteraction user={self.user_id} product={self.product_id} type={self.interaction_type}>"


class ProductRecommendation(Base):
    """A product recommendation generated for a specific user."""

    __tablename__ = "product_recommendations"

    id = Column(UUID(native_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(native_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(native_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # Relevance score 0.0 – 1.0
    reason = Column(String, nullable=True)  # Human-readable reason
    source_pin_id = Column(String, nullable=True)  # Pinterest pin that drove the recommendation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="recommendations")
    product = relationship("Product", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<ProductRecommendation user={self.user_id} product={self.product_id} score={self.score}>"
