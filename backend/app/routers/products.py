"""Products router: recommendations, search, click tracking, product detail."""

import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
import sqlalchemy as sa
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse, RecommendationResponse
from app.services import auth_service
from app.services.affiliate_service import track_click
from app.services.recommendation_service import get_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def get_product_recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None),
    color: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[RecommendationResponse]:
    """Return personalised product recommendations for the authenticated user.

    Supports filtering by category, color, brand, and price range.
    """
    recs = await get_recommendations(
        user_id=current_user.id,
        db=db,
        limit=limit,
        offset=offset,
        category=category,
        color=color,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
    )
    return [RecommendationResponse.model_validate(r) for r in recs]


@router.get("/search", response_model=list[ProductResponse])
async def search_products(
    q: str | None = Query(default=None, description="Free-text query"),
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    color: str | None = Query(default=None),
    size: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(auth_service.get_current_user),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),
) -> list[ProductResponse]:
    """Search products with optional filters."""
    from sqlalchemy import and_

    conditions = []
    if q:
        conditions.append(
            or_(
                Product.title.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%"),
                Product.brand.ilike(f"%{q}%"),
            )
        )
    if category:
        conditions.append(Product.category.ilike(f"%{category}%"))
    if brand:
        conditions.append(Product.brand.ilike(f"%{brand}%"))
    if color:
        conditions.append(Product.colors.cast(sa.Text).ilike(f"%{color.lower()}%"))
    if size:
        conditions.append(Product.sizes.cast(sa.Text).ilike(f"%{size.lower()}%"))
    if min_price is not None:
        conditions.append(Product.price >= min_price)
    if max_price is not None:
        conditions.append(Product.price <= max_price)

    stmt = select(Product)
    if conditions:
        from sqlalchemy import and_
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    products = result.scalars().all()
    return [ProductResponse.model_validate(p) for p in products]


class ClickBody:
    """Request body for POST /products/track-click."""

    def __init__(self, product_id: UUID, session_id: str | None = None, referrer_pin_id: str | None = None):
        self.product_id = product_id
        self.session_id = session_id
        self.referrer_pin_id = referrer_pin_id


@router.post("/track-click", status_code=status.HTTP_204_NO_CONTENT)
async def track_product_click(
    product_id: UUID,
    session_id: str | None = Query(default=None),
    referrer_pin_id: str | None = Query(default=None),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Record an affiliate click event for analytics and attribution."""
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await track_click(
        user_id=current_user.id,
        product_id=product_id,
        db=db,
        session_id=session_id,
        referrer_pin_id=referrer_pin_id,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: User = Depends(auth_service.get_current_user),  # noqa: ARG001
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """Return details for a single product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)
