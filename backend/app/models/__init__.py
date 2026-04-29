"""Import all ORM models so Alembic and SQLAlchemy can discover them."""

from app.models.user import User
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.product import Product
from app.models.interaction import UserInteraction, ProductRecommendation

__all__ = [
    "User",
    "PinterestBoard",
    "PinterestPin",
    "Product",
    "UserInteraction",
    "ProductRecommendation",
]
