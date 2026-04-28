"""Product similarity matching using cosine similarity and weighted scoring."""

import hashlib
import logging
from typing import Any

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.utils.cache import cache_get, cache_set, recommendations_cache_key

logger = logging.getLogger(__name__)

# Scoring weights must sum to 1.0
WEIGHTS = {
    "style": 0.40,
    "color": 0.30,
    "type": 0.20,
    "brand": 0.10,
}


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return cosine similarity in [0, 1] between two vectors."""
    va, vb = np.array(a, dtype=np.float32), np.array(b, dtype=np.float32)
    norm_a, norm_b = np.linalg.norm(va), np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def _score_product(product: Product, query: dict[str, Any]) -> float:
    """Compute a weighted relevance score for *product* against *query* analysis."""
    score = 0.0

    # Style similarity
    product_styles: set[str] = set(
        (product.embedding or [])[:0]  # placeholder; real embedding below
    )
    query_styles: list[str] = query.get("styles", [])
    if query_styles and product.embedding:
        # Use vector similarity if embedding available
        query_vec = query.get("embedding")
        if query_vec and len(query_vec) == len(product.embedding):
            sim = _cosine_similarity(product.embedding, query_vec)
            score += WEIGHTS["style"] * sim
    else:
        # Fallback: category text match
        if product.category:
            clothing = query.get("clothing_type", "")
            if clothing and clothing.lower() in product.category.lower():
                score += WEIGHTS["style"]

    # Color match
    query_colors: list[str] = query.get("colors", [])
    product_colors: list[str] = product.colors or []
    if query_colors and product_colors:
        overlap = len(set(query_colors) & set(c.lower() for c in product_colors))
        color_score = min(1.0, overlap / max(len(query_colors), 1))
        score += WEIGHTS["color"] * color_score

    # Clothing type match
    clothing_type = query.get("clothing_type")
    if clothing_type and product.category:
        if clothing_type.lower() in product.category.lower():
            score += WEIGHTS["type"]

    # Brand preference
    preferred_brands: list[str] = [b.lower() for b in query.get("detected_brands", [])]
    if preferred_brands and product.brand:
        if product.brand.lower() in preferred_brands:
            score += WEIGHTS["brand"]

    return round(score, 4)


class ProductMatchingService:
    async def get_recommendations(
        self,
        db: AsyncSession,
        pin_analyses: list[dict[str, Any]],
        user_id: str,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Given a list of pin analysis results, return ranked product recommendations.

        Applies optional filters: price_min, price_max, category, colors.
        """
        filters = filters or {}
        cache_key = recommendations_cache_key(
            user_id, self._filters_hash(pin_analyses, filters)
        )
        cached = await cache_get(cache_key)
        if cached:
            return cached[offset : offset + limit]

        # Aggregate query profile from multiple pin analyses
        query_profile = self._aggregate_query_profile(pin_analyses)

        # Fetch candidate products from DB
        products = await self._fetch_candidates(db, filters)

        # Score and rank
        scored: list[tuple[float, Product]] = []
        for product in products:
            score = _score_product(product, query_profile)
            scored.append((score, product))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [self._product_to_dict(p, s) for s, p in scored]

        await cache_set(cache_key, results, ttl=600)
        return results[offset : offset + limit]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate_query_profile(analyses: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple pin analyses into a single query profile."""
        all_colors: list[str] = []
        all_styles: list[str] = []
        all_brands: list[str] = []
        clothing_types: list[str] = []

        for a in analyses:
            all_colors.extend(a.get("colors", []))
            all_styles.extend(a.get("styles", []))
            all_brands.extend(a.get("detected_brands", []))
            ct = a.get("clothing_type")
            if ct:
                clothing_types.append(ct)

        def most_common(lst: list[str], top: int = 5) -> list[str]:
            from collections import Counter
            return [item for item, _ in Counter(lst).most_common(top)]

        return {
            "colors": most_common(all_colors),
            "styles": most_common(all_styles),
            "detected_brands": most_common(all_brands),
            "clothing_type": most_common(clothing_types, 1)[0] if clothing_types else None,
        }

    @staticmethod
    async def _fetch_candidates(
        db: AsyncSession, filters: dict[str, Any]
    ) -> list[Product]:
        stmt = select(Product)

        price_min = filters.get("price_min")
        price_max = filters.get("price_max")
        category = filters.get("category")
        colors = filters.get("colors")

        if price_min is not None:
            stmt = stmt.where(Product.price >= price_min)
        if price_max is not None:
            stmt = stmt.where(Product.price <= price_max)
        if category:
            stmt = stmt.where(Product.category.ilike(f"%{category}%"))
        if colors:
            from sqlalchemy import cast
            from sqlalchemy.dialects.postgresql import ARRAY
            from sqlalchemy import String
            stmt = stmt.where(Product.colors.overlap(cast(colors, ARRAY(String))))

        result = await db.execute(stmt.limit(500))
        return list(result.scalars().all())

    @staticmethod
    def _product_to_dict(product: Product, score: float) -> dict[str, Any]:
        return {
            "id": str(product.id),
            "retailer_id": product.retailer_id,
            "retailer_name": product.retailer_name,
            "title": product.title,
            "price": float(product.price) if product.price else None,
            "currency": product.currency,
            "image_url": product.image_url,
            "product_url": product.product_url,
            "affiliate_url": product.affiliate_url,
            "category": product.category,
            "brand": product.brand,
            "colors": product.colors or [],
            "sizes": product.sizes or [],
            "relevance_score": score,
        }

    @staticmethod
    def _filters_hash(analyses: list[dict], filters: dict) -> str:
        import json
        raw = json.dumps({"analyses": analyses, "filters": filters}, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()[:16]


product_matching_service = ProductMatchingService()
