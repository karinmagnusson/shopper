import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.product import Product, UserInteraction
from app.schemas.product import InteractionCreate, ProductFilter, ProductRead
from app.services.product_matching import ProductMatchingService
from app.services.affiliate import AffiliateService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
async def get_recommendations(
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = ProductFilter(
        price_min=price_min,
        price_max=price_max,
        category=category,
        color=color,
        brand=brand,
        style=style,
    )
    products = await ProductMatchingService.get_recommendations(
        db, current_user, filters, limit
    )
    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi import HTTPException, status

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/{product_id}/interact")
async def record_interaction(
    product_id: str,
    body: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interaction = UserInteraction(
        user_id=current_user.id,
        product_id=product_id,
        interaction_type=body.interaction_type,
    )
    db.add(interaction)
    db.commit()
    return {"status": "recorded"}


@router.get("/{product_id}/affiliate-link")
async def get_affiliate_link(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi import HTTPException, status

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    url = AffiliateService.generate_url(
        product.product_url or "", product.retailer_name or "unknown"
    )
    return {"url": url}
