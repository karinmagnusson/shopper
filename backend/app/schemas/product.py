"""Pydantic schemas for Products and Recommendations."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProductResponse(BaseModel):
    """Serialised product."""

    model_config = {"from_attributes": True}

    id: UUID
    title: str
    description: str | None = None
    brand: str | None = None
    category: str | None = None
    price: Decimal | None = None
    currency: str = "USD"
    image_url: str | None = None
    affiliate_url: str
    colors: list[str] = []
    sizes: list[str] = []
    style_tags: list[str] = []
    rating: Decimal | None = None
    review_count: int = 0


class ProductSearchRequest(BaseModel):
    """Filters for product search."""

    query: str | None = None
    category: str | None = None
    brand: str | None = None
    color: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    size: str | None = None
    limit: int = 20
    offset: int = 0


class RecommendationResponse(BaseModel):
    """A recommendation entry linking a product to a score."""

    model_config = {"from_attributes": True}

    id: UUID
    product: ProductResponse
    score: float
    reason: str | None = None
    source_pin_id: str | None = None
