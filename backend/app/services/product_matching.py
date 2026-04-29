import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.pinterest import PinterestPin
from app.models.product import Product
from app.schemas.product import ProductFilter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock product catalogue – used when no real retailer API is configured
# ---------------------------------------------------------------------------
_MOCK_PRODUCTS: list[dict[str, Any]] = [
    {"id": "p1", "title": "Floral Wrap Dress", "price": 59.99, "category": "dress", "brand": "Zara", "colors": ["pink", "white"], "style_tags": ["romantic", "bohemian"], "retailer_name": "Zara", "image_url": "https://picsum.photos/400/600?random=10", "product_url": "https://zara.com/p1"},
    {"id": "p2", "title": "Classic White Blazer", "price": 89.99, "category": "jacket", "brand": "H&M", "colors": ["white"], "style_tags": ["minimalist", "formal"], "retailer_name": "H&M", "image_url": "https://picsum.photos/400/600?random=11", "product_url": "https://hm.com/p2"},
    {"id": "p3", "title": "High-Rise Straight Jeans", "price": 79.00, "category": "jeans", "brand": "Levi's", "colors": ["blue", "navy"], "style_tags": ["casual", "streetwear"], "retailer_name": "Levi's", "image_url": "https://picsum.photos/400/600?random=12", "product_url": "https://levis.com/p3"},
    {"id": "p4", "title": "Silk Cami Top", "price": 45.00, "category": "top", "brand": "& Other Stories", "colors": ["beige", "neutral"], "style_tags": ["minimalist", "romantic"], "retailer_name": "& Other Stories", "image_url": "https://picsum.photos/400/600?random=13", "product_url": "https://stories.com/p4"},
    {"id": "p5", "title": "Oversized Trench Coat", "price": 149.00, "category": "coat", "brand": "Mango", "colors": ["beige", "brown"], "style_tags": ["minimalist", "formal"], "retailer_name": "Mango", "image_url": "https://picsum.photos/400/600?random=14", "product_url": "https://mango.com/p5"},
    {"id": "p6", "title": "Leather Mini Skirt", "price": 69.00, "category": "skirt", "brand": "ASOS", "colors": ["black"], "style_tags": ["edgy", "streetwear"], "retailer_name": "ASOS", "image_url": "https://picsum.photos/400/600?random=15", "product_url": "https://asos.com/p6"},
    {"id": "p7", "title": "Strappy Sandals", "price": 55.00, "category": "shoes", "brand": "Steve Madden", "colors": ["beige", "nude"], "style_tags": ["casual", "romantic"], "retailer_name": "Steve Madden", "image_url": "https://picsum.photos/400/600?random=16", "product_url": "https://stevemadden.com/p7"},
    {"id": "p8", "title": "Chunky Knit Sweater", "price": 65.00, "category": "top", "brand": "Weekday", "colors": ["beige", "grey"], "style_tags": ["casual", "minimalist"], "retailer_name": "Weekday", "image_url": "https://picsum.photos/400/600?random=17", "product_url": "https://weekday.com/p8"},
    {"id": "p9", "title": "Printed Midi Skirt", "price": 49.00, "category": "skirt", "brand": "Topshop", "colors": ["pink", "floral"], "style_tags": ["bohemian", "romantic"], "retailer_name": "Topshop", "image_url": "https://picsum.photos/400/600?random=18", "product_url": "https://topshop.com/p9"},
    {"id": "p10", "title": "Structured Tote Bag", "price": 119.00, "category": "bag", "brand": "Charles & Keith", "colors": ["black", "brown"], "style_tags": ["minimalist", "formal"], "retailer_name": "Charles & Keith", "image_url": "https://picsum.photos/400/600?random=19", "product_url": "https://charleskeith.com/p10"},
    {"id": "p11", "title": "Cropped Denim Jacket", "price": 85.00, "category": "jacket", "brand": "Wrangler", "colors": ["blue", "navy"], "style_tags": ["casual", "streetwear"], "retailer_name": "Wrangler", "image_url": "https://picsum.photos/400/600?random=20", "product_url": "https://wrangler.com/p11"},
    {"id": "p12", "title": "Slip Dress", "price": 39.00, "category": "dress", "brand": "SHEIN", "colors": ["black", "red"], "style_tags": ["edgy", "romantic"], "retailer_name": "SHEIN", "image_url": "https://picsum.photos/400/600?random=21", "product_url": "https://shein.com/p12"},
]


def _dict_to_product(d: dict[str, Any]) -> Product:
    p = Product()
    p.id = uuid.UUID(int=int(d["id"][1:]) * 10**30 % (2**128))
    p.title = d["title"]
    p.price = d["price"]
    p.category = d["category"]
    p.brand = d["brand"]
    p.colors = d["colors"]
    p.style_tags = d["style_tags"]
    p.retailer_name = d["retailer_name"]
    p.image_url = d["image_url"]
    p.product_url = d["product_url"]
    p.affiliate_url = d["product_url"] + "?ref=shopper"
    return p


class ProductMatchingService:
    @staticmethod
    async def get_recommendations(
        db: Session,
        user: User,
        filters: ProductFilter,
        limit: int = 20,
    ) -> list[Product]:
        # Collect analysis data from user's pins
        from app.models.pinterest import PinterestBoard, PinterestPin

        boards = db.query(PinterestBoard).filter(PinterestBoard.user_id == user.id).all()
        board_ids = [b.id for b in boards]

        pins_with_analysis: list[dict] = []
        if board_ids:
            pins = (
                db.query(PinterestPin)
                .filter(
                    PinterestPin.board_id.in_(board_ids),
                    PinterestPin.analysis_data.isnot(None),
                )
                .limit(50)
                .all()
            )
            pins_with_analysis = [p.analysis_data for p in pins if p.analysis_data]

        # Aggregate style profile from pins
        style_profile: dict[str, list[str]] = {"colors": [], "clothing_types": [], "styles": []}
        for data in pins_with_analysis:
            style_profile["colors"].extend(data.get("colors", []))
            style_profile["clothing_types"].extend(data.get("clothing_types", []))
            style_profile["styles"].extend(data.get("styles", []))

        # Try DB products first
        query = db.query(Product)
        if filters.price_min is not None:
            query = query.filter(Product.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.filter(Product.price <= filters.price_max)
        if filters.category:
            query = query.filter(Product.category == filters.category)
        if filters.brand:
            query = query.filter(Product.brand.ilike(f"%{filters.brand}%"))

        db_products = query.limit(limit).all()
        if db_products:
            return _rank_products(db_products, style_profile, filters)[:limit]

        # Fall back to mock catalogue
        candidates = [_dict_to_product(d) for d in _MOCK_PRODUCTS]
        candidates = _apply_filters(candidates, filters)
        return _rank_products(candidates, style_profile, filters)[:limit]


def _apply_filters(products: list[Product], f: ProductFilter) -> list[Product]:
    result = []
    for p in products:
        if f.price_min and (p.price or 0) < f.price_min:
            continue
        if f.price_max and (p.price or 0) > f.price_max:
            continue
        if f.category and p.category != f.category:
            continue
        if f.brand and f.brand.lower() not in (p.brand or "").lower():
            continue
        if f.color and f.color not in (p.colors or []):
            continue
        if f.style and f.style not in (p.style_tags or []):
            continue
        result.append(p)
    return result


def _rank_products(
    products: list[Product],
    profile: dict[str, list[str]],
    filters: ProductFilter,
) -> list[Product]:
    def score(p: Product) -> float:
        s = 0.0
        p_colors = set(p.colors or [])
        p_types = {p.category} if p.category else set()
        p_styles = set(p.style_tags or [])

        profile_colors = set(profile["colors"])
        profile_types = set(profile["clothing_types"])
        profile_styles = set(profile["styles"])

        if profile_colors & p_colors:
            s += 0.30
        if profile_types & p_types:
            s += 0.20
        if profile_styles & p_styles:
            s += 0.40
        return s

    return sorted(products, key=score, reverse=True)
