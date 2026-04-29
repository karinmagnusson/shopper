import logging
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from app.core.config import settings

logger = logging.getLogger(__name__)

_RETAILER_PARAMS: dict[str, dict[str, str]] = {
    "amazon": {"tag": settings.AMAZON_ASSOCIATE_TAG or "shopper-20"},
    "default": {"ref": "shopper", "utm_source": "shopper", "utm_medium": "affiliate"},
}


class AffiliateService:
    @staticmethod
    def generate_url(product_url: str, retailer: str) -> str:
        if not product_url:
            return ""
        retailer_key = retailer.lower()
        params = _RETAILER_PARAMS.get(retailer_key, _RETAILER_PARAMS["default"])
        parsed = urlparse(product_url)
        existing = parse_qs(parsed.query)
        existing.update({k: [v] for k, v in params.items()})
        new_query = urlencode({k: v[0] for k, v in existing.items()})
        return urlunparse(parsed._replace(query=new_query))

    @staticmethod
    def track_click(user_id: str, product_id: str) -> None:
        logger.info("Affiliate click: user=%s product=%s", user_id, product_id)
