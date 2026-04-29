import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    retailer_name: str | None
    title: str
    price: Decimal | None
    image_url: str | None
    product_url: str | None
    affiliate_url: str | None
    category: str | None
    brand: str | None
    colors: list[str] | None
    sizes: list[str] | None
    style_tags: list[str] | None


class ProductFilter(BaseModel):
    price_min: float | None = None
    price_max: float | None = None
    category: str | None = None
    color: str | None = None
    brand: str | None = None
    style: str | None = None


class InteractionCreate(BaseModel):
    interaction_type: str  # view, click, save, purchase
