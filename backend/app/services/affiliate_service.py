"""Affiliate link generation and click tracking service."""

import hashlib
import logging
from urllib.parse import urlencode, urljoin, urlparse, urlunparse, parse_qs, ParseResult
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.interaction import UserInteraction

logger = logging.getLogger(__name__)


def _build_tracking_tag(user_id: UUID, product_id: UUID) -> str:
    """Create a deterministic short tracking tag from user + product IDs.

    Args:
        user_id: UUID of the user.
        product_id: UUID of the product.

    Returns:
        8-character hex digest string.
    """
    combined = f"{user_id}:{product_id}"
    return hashlib.sha256(combined.encode()).hexdigest()[:8]


def generate_amazon_affiliate_url(asin: str, user_id: UUID, product_id: UUID) -> str:
    """Generate an Amazon Associates affiliate URL with tracking tag.

    Args:
        asin: Amazon Standard Identification Number.
        user_id: UUID of the user clicking.
        product_id: UUID of the product.

    Returns:
        Full Amazon affiliate URL string.
    """
    if not settings.AMAZON_ASSOCIATE_TAG:
        return f"https://www.amazon.com/dp/{asin}"

    tracking = _build_tracking_tag(user_id, product_id)
    params = urlencode({
        "tag": settings.AMAZON_ASSOCIATE_TAG,
        "linkCode": "as2",
        "creative": "9325",
        "creativeASIN": asin,
        "ref": f"shopper_{tracking}",
    })
    return f"https://www.amazon.com/dp/{asin}?{params}"


def generate_generic_affiliate_url(
    base_url: str,
    user_id: UUID,
    product_id: UUID,
    extra_params: dict | None = None,
) -> str:
    """Append affiliate tracking parameters to any generic product URL.

    Args:
        base_url: Original product landing page URL.
        user_id: UUID of the user.
        product_id: UUID of the product.
        extra_params: Additional query parameters to merge in.

    Returns:
        Modified URL string with tracking parameters appended.
    """
    parsed: ParseResult = urlparse(base_url)
    tracking = _build_tracking_tag(user_id, product_id)

    new_params: dict = extra_params or {}
    new_params["ref"] = f"shopper_{tracking}"
    new_params["utm_source"] = "shopper"
    new_params["utm_medium"] = "affiliate"

    existing_qs = parse_qs(parsed.query)
    existing_qs.update({k: [v] for k, v in new_params.items()})

    flat_qs = {k: v[0] for k, v in existing_qs.items()}
    new_query = urlencode(flat_qs)

    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)


async def track_click(
    user_id: UUID,
    product_id: UUID,
    db: AsyncSession,
    session_id: str | None = None,
    referrer_pin_id: str | None = None,
) -> UserInteraction:
    """Record an affiliate click event in the database.

    Args:
        user_id: UUID of the clicking user.
        product_id: UUID of the product clicked.
        db: Async DB session.
        session_id: Optional browser session identifier.
        referrer_pin_id: Pinterest pin ID that led to the click.

    Returns:
        The persisted UserInteraction ORM object.
    """
    interaction = UserInteraction(
        user_id=user_id,
        product_id=product_id,
        interaction_type="click",
        session_id=session_id,
        referrer_pin_id=referrer_pin_id,
    )
    db.add(interaction)
    await db.flush()
    logger.info("Tracked click: user=%s product=%s", user_id, product_id)
    return interaction
