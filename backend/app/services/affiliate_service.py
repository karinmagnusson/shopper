"""Affiliate link management and click tracking."""

import logging
import urllib.parse
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.interaction import UserInteraction

logger = logging.getLogger(__name__)


class AffiliateService:
    """Generate affiliate links and record interaction events."""

    def generate_amazon_link(self, product_url: str) -> str:
        """
        Append the Amazon Associates tag to a product URL.

        Handles both short (amzn.to) and full Amazon URLs.
        """
        try:
            parsed = urllib.parse.urlparse(product_url)
            query = dict(urllib.parse.parse_qsl(parsed.query))
            query["tag"] = settings.AMAZON_ASSOCIATE_TAG
            new_query = urllib.parse.urlencode(query)
            affiliate = parsed._replace(query=new_query)
            return urllib.parse.urlunparse(affiliate)
        except Exception as exc:
            logger.warning("Failed to generate Amazon affiliate link: %s", exc)
            return product_url

    def enrich_product(self, product: dict[str, Any]) -> dict[str, Any]:
        """Add or replace affiliate_url on a product dict."""
        retailer = (product.get("retailer_name") or "").lower()
        url = product.get("product_url", "")

        if "amazon" in retailer or "amzn" in url:
            product["affiliate_url"] = self.generate_amazon_link(url)
        else:
            # For other retailers, pass through unchanged (extensible)
            product["affiliate_url"] = product.get("affiliate_url") or url

        return product

    async def track_click(
        self,
        db: AsyncSession,
        user_id: str,
        product_id: str,
        interaction_type: str = "click",
    ) -> None:
        """Persist a user interaction event."""
        import uuid

        interaction = UserInteraction(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            product_id=uuid.UUID(product_id),
            interaction_type=interaction_type,
        )
        db.add(interaction)
        try:
            await db.commit()
        except Exception as exc:
            await db.rollback()
            logger.error("Failed to track interaction: %s", exc)
            raise


affiliate_service = AffiliateService()
