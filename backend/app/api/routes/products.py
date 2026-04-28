"""Product recommendation and search endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Body, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models.pinterest import PinterestBoard, PinterestPin
from app.services.affiliate_service import affiliate_service
from app.services.product_matching import product_matching_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/recommendations")
async def get_recommendations(
    current_user: CurrentUser,
    db: DBSession,
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    category: str | None = Query(None, max_length=100),
    colors: list[str] | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """
    Return product recommendations based on analysed pins from the user's boards.
    """
    # Gather all analyses for the user's analysed pins
    boards_result = await db.execute(
        select(PinterestBoard).where(PinterestBoard.user_id == current_user.id)
    )
    board_ids = [b.id for b in boards_result.scalars().all()]

    analyses: list[dict] = []
    if board_ids:
        pins_result = await db.execute(
            select(PinterestPin).where(
                PinterestPin.board_id.in_(board_ids),
                PinterestPin.analysis_data.isnot(None),
            )
        )
        analyses = [p.analysis_data for p in pins_result.scalars().all() if p.analysis_data]

    filters = {}
    if price_min is not None:
        filters["price_min"] = price_min
    if price_max is not None:
        filters["price_max"] = price_max
    if category:
        filters["category"] = category
    if colors:
        filters["colors"] = colors

    recommendations = await product_matching_service.get_recommendations(
        db=db,
        pin_analyses=analyses,
        user_id=str(current_user.id),
        filters=filters,
        limit=limit,
        offset=offset,
    )

    # Enrich with affiliate links
    recommendations = [affiliate_service.enrich_product(r) for r in recommendations]

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "offset": offset,
        "limit": limit,
    }


@router.get("/search")
async def search_products(
    current_user: CurrentUser,
    db: DBSession,
    q: str | None = Query(None, max_length=255),
    category: str | None = Query(None, max_length=100),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    colors: list[str] | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """Search products with optional filters."""
    from app.models.product import Product
    from sqlalchemy import or_

    stmt = select(Product)
    if q:
        stmt = stmt.where(
            or_(
                Product.title.ilike(f"%{q}%"),
                Product.brand.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%"),
            )
        )
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    if price_min is not None:
        stmt = stmt.where(Product.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Product.price <= price_max)

    result = await db.execute(stmt.offset(offset).limit(limit))
    products = result.scalars().all()

    return {
        "products": [
            affiliate_service.enrich_product(
                {
                    "id": str(p.id),
                    "retailer_name": p.retailer_name,
                    "title": p.title,
                    "price": float(p.price) if p.price else None,
                    "currency": p.currency,
                    "image_url": p.image_url,
                    "product_url": p.product_url,
                    "affiliate_url": p.affiliate_url,
                    "category": p.category,
                    "brand": p.brand,
                    "colors": p.colors or [],
                    "sizes": p.sizes or [],
                }
            )
            for p in products
        ],
        "total": len(products),
        "offset": offset,
        "limit": limit,
    }


@router.post("/track-click", status_code=201)
async def track_click(
    current_user: CurrentUser,
    db: DBSession,
    product_id: Annotated[str, Body(embed=True)],
    interaction_type: Annotated[str, Body(embed=True)] = "click",
) -> dict:
    """Record a user interaction (click, save, etc.) on a product."""
    await affiliate_service.track_click(
        db=db,
        user_id=str(current_user.id),
        product_id=product_id,
        interaction_type=interaction_type,
    )
    return {"status": "tracked"}
