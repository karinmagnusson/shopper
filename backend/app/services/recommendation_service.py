"""Product recommendation engine."""

import logging
import sqlalchemy as sa
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interaction import ProductRecommendation
from app.models.pinterest import PinterestBoard, PinterestPin
from app.models.product import Product

logger = logging.getLogger(__name__)

# Scoring weights must sum to 1.0
WEIGHT_COLOR = 0.30
WEIGHT_STYLE = 0.40
WEIGHT_CATEGORY = 0.20
WEIGHT_BRAND = 0.10


def _color_similarity(pin_colors: list[str], product_colors: list[str]) -> float:
    """Return proportion of pin colors that appear in the product palette.

    Args:
        pin_colors: Dominant colors from pin analysis (hex strings).
        product_colors: Colors listed on the product.

    Returns:
        Float in [0.0, 1.0].
    """
    if not pin_colors or not product_colors:
        return 0.0
    pin_set = {c.lower() for c in pin_colors}
    prod_set = {c.lower() for c in product_colors}
    matches = len(pin_set & prod_set)
    return matches / len(pin_set)


def _style_similarity(pin_styles: list[str], product_tags: list[str]) -> float:
    """Return proportion of pin style tags that appear in the product tags.

    Args:
        pin_styles: Style tags from pin analysis.
        product_tags: Style tags on the product.

    Returns:
        Float in [0.0, 1.0].
    """
    if not pin_styles or not product_tags:
        return 0.0
    pin_set = {s.lower() for s in pin_styles}
    prod_set = {s.lower() for s in product_tags}
    matches = len(pin_set & prod_set)
    return matches / len(pin_set)


def _category_match(pin_categories: list[str], product_category: str | None) -> float:
    """Return 1.0 if product category is among pin categories, else 0.0.

    Args:
        pin_categories: Fashion categories from pin analysis.
        product_category: Product category string.

    Returns:
        Float 0.0 or 1.0.
    """
    if not product_category or not pin_categories:
        return 0.0
    return 1.0 if product_category.lower() in [c.lower() for c in pin_categories] else 0.0


def score_product(analysis: dict, product: Product, preferred_brands: list[str] | None = None) -> float:
    """Compute a weighted relevance score for a product against a pin analysis.

    Args:
        analysis: FashionAnalysis dict (from pin.analysis_data).
        product: Product ORM instance.
        preferred_brands: User's preferred brand names from style_preferences.

    Returns:
        Float score in [0.0, 1.0].
    """
    colors = analysis.get("colors", [])
    style_tags = analysis.get("style_tags", [])
    categories = analysis.get("categories", [])

    color_score = _color_similarity(colors, list(product.colors or []))
    style_score = _style_similarity(style_tags, list(product.style_tags or []))
    category_score = _category_match(categories, product.category)

    brand_score = 0.0
    if preferred_brands and product.brand:
        brand_score = 1.0 if product.brand.lower() in [b.lower() for b in preferred_brands] else 0.0

    total = (
        color_score * WEIGHT_COLOR
        + style_score * WEIGHT_STYLE
        + category_score * WEIGHT_CATEGORY
        + brand_score * WEIGHT_BRAND
    )
    return round(min(total, 1.0), 4)


async def generate_recommendations_for_user(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 50,
) -> list[ProductRecommendation]:
    """Generate and persist product recommendations for a user.

    Pulls all analysed pins for the user, scores every available product
    against the aggregate analysis, and persists the top-N recommendations.

    Args:
        user_id: UUID of the target user.
        db: Async DB session.
        limit: Maximum number of recommendations to store.

    Returns:
        List of persisted ProductRecommendation ORM objects.
    """
    from app.models.user import User

    # Load user with preferences
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        logger.error("User %s not found when generating recommendations", user_id)
        return []

    preferred_brands: list[str] = user.style_preferences.get("brands", []) if user.style_preferences else []

    # Collect all analysed pins for this user
    boards_result = await db.execute(
        select(PinterestBoard)
        .where(PinterestBoard.user_id == user_id)
        .options(selectinload(PinterestBoard.pins))
    )
    boards = boards_result.scalars().all()
    analysed_pins = [
        pin for board in boards for pin in board.pins if pin.analysis_data
    ]

    if not analysed_pins:
        logger.info("No analysed pins found for user %s", user_id)
        return []

    # Aggregate analysis signals across all pins
    agg_colors: dict[str, int] = {}
    agg_styles: dict[str, int] = {}
    agg_categories: dict[str, int] = {}

    for pin in analysed_pins:
        data = pin.analysis_data or {}
        for c in data.get("colors", []):
            agg_colors[c] = agg_colors.get(c, 0) + 1
        for s in data.get("style_tags", []):
            agg_styles[s] = agg_styles.get(s, 0) + 1
        for cat in data.get("categories", []):
            agg_categories[cat] = agg_categories.get(cat, 0) + 1

    # Build aggregate "virtual" analysis
    top_colors = sorted(agg_colors, key=lambda k: agg_colors[k], reverse=True)[:5]
    top_styles = sorted(agg_styles, key=lambda k: agg_styles[k], reverse=True)[:5]
    top_categories = sorted(agg_categories, key=lambda k: agg_categories[k], reverse=True)[:3]

    aggregate_analysis = {
        "colors": top_colors,
        "style_tags": top_styles,
        "categories": top_categories,
    }

    # Score all products
    products_result = await db.execute(select(Product))
    all_products = products_result.scalars().all()

    scored: list[tuple[float, Product]] = []
    for product in all_products:
        s = score_product(aggregate_analysis, product, preferred_brands)
        if s > 0.0:
            scored.append((s, product))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_products = scored[:limit]

    # Delete existing recommendations for user and replace
    existing = await db.execute(
        select(ProductRecommendation).where(ProductRecommendation.user_id == user_id)
    )
    for old_rec in existing.scalars().all():
        await db.delete(old_rec)

    new_recs: list[ProductRecommendation] = []
    for sc, product in top_products:
        reason = _build_reason(aggregate_analysis, product, sc)
        rec = ProductRecommendation(
            user_id=user_id,
            product_id=product.id,
            score=sc,
            reason=reason,
        )
        db.add(rec)
        new_recs.append(rec)

    await db.flush()
    logger.info("Generated %d recommendations for user %s", len(new_recs), user_id)
    return new_recs


def _build_reason(analysis: dict, product: Product, score: float) -> str:
    """Build a human-readable reason string for a recommendation.

    Args:
        analysis: Aggregated analysis dict.
        product: The recommended product.
        score: Computed relevance score.

    Returns:
        Short explanation string.
    """
    reasons: list[str] = []
    if analysis.get("categories") and product.category:
        if product.category.lower() in [c.lower() for c in analysis["categories"]]:
            reasons.append(f"matches your {product.category} style")
    if analysis.get("style_tags") and product.style_tags:
        common = set(analysis["style_tags"]) & set(product.style_tags)
        if common:
            reasons.append(f"fits your {', '.join(list(common)[:2])} aesthetic")
    if analysis.get("colors") and product.colors:
        common_colors = set(analysis["colors"]) & set(product.colors)
        if common_colors:
            reasons.append("complements your color palette")

    if not reasons:
        return "Recommended based on your Pinterest style"
    return "Because it " + " and ".join(reasons)


async def get_recommendations(
    user_id: UUID,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    category: str | None = None,
    color: str | None = None,
    brand: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> list[ProductRecommendation]:
    """Retrieve persisted recommendations for a user with optional filters.

    Args:
        user_id: Target user UUID.
        db: Async DB session.
        limit: Page size.
        offset: Page offset.
        category: Filter by product category.
        color: Filter by color in product colors array.
        brand: Filter by brand name.
        min_price: Minimum product price filter.
        max_price: Maximum product price filter.

    Returns:
        Filtered list of ProductRecommendation ORM objects (ordered by score).
    """
    from sqlalchemy import and_

    stmt = (
        select(ProductRecommendation)
        .join(ProductRecommendation.product)
        .where(ProductRecommendation.user_id == user_id)
        .options(selectinload(ProductRecommendation.product))
        .order_by(ProductRecommendation.score.desc())
    )

    filters = []
    if category:
        filters.append(Product.category.ilike(f"%{category}%"))
    if brand:
        filters.append(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    if color:
        filters.append(Product.colors.cast(sa.Text).ilike(f"%{color.lower()}%"))

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
