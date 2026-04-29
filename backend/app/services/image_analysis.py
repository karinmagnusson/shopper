import logging
import random
from typing import Any

logger = logging.getLogger(__name__)

_COLORS = ["black", "white", "navy", "beige", "red", "pink", "green", "brown", "grey", "blue"]
_CLOTHING = ["dress", "top", "pants", "jeans", "skirt", "jacket", "coat", "shoes", "bag", "accessories"]
_STYLES = ["casual", "formal", "bohemian", "minimalist", "streetwear", "preppy", "romantic", "edgy"]


class ImageAnalysisService:
    @staticmethod
    async def analyze_image(image_url: str) -> dict[str, Any]:
        """
        Analyze a fashion image and return style metadata.
        Falls back to plausible mock data when Google Vision API is not configured.
        """
        from app.core.config import settings

        if settings.GOOGLE_VISION_API_KEY:
            return await ImageAnalysisService._analyze_with_vision(image_url)
        return ImageAnalysisService._mock_analysis(image_url)

    @staticmethod
    def _mock_analysis(image_url: str) -> dict[str, Any]:
        seed = sum(ord(c) for c in image_url) % 100
        rng = random.Random(seed)
        return {
            "colors": rng.sample(_COLORS, k=3),
            "clothing_types": rng.sample(_CLOTHING, k=2),
            "styles": rng.sample(_STYLES, k=2),
            "confidence": round(rng.uniform(0.65, 0.95), 2),
            "source": "mock",
        }

    @staticmethod
    async def _analyze_with_vision(image_url: str) -> dict[str, Any]:
        try:
            import httpx
            from app.core.config import settings

            payload = {
                "requests": [
                    {
                        "image": {"source": {"imageUri": image_url}},
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 20},
                            {"type": "IMAGE_PROPERTIES"},
                        ],
                    }
                ]
            }
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://vision.googleapis.com/v1/images:annotate",
                    params={"key": settings.GOOGLE_VISION_API_KEY},
                    json=payload,
                )
            if not resp.is_success:
                logger.warning("Vision API error %s, falling back to mock", resp.status_code)
                return ImageAnalysisService._mock_analysis(image_url)

            data = resp.json()
            response = data.get("responses", [{}])[0]
            labels = [la["description"].lower() for la in response.get("labelAnnotations", [])]
            colors = _extract_colors(response.get("imagePropertiesAnnotation", {}))
            clothing_types = [l for l in labels if l in _CLOTHING]
            styles = [l for l in labels if l in _STYLES]
            return {
                "colors": colors[:3] or ["unknown"],
                "clothing_types": clothing_types[:3] or ["clothing"],
                "styles": styles[:3] or ["casual"],
                "confidence": 0.85,
                "source": "google_vision",
                "labels": labels[:10],
            }
        except Exception as exc:
            logger.warning("Vision API exception: %s, falling back to mock", exc)
            return ImageAnalysisService._mock_analysis(image_url)


def _extract_colors(props: dict) -> list[str]:
    dominant = props.get("dominantColors", {}).get("colors", [])
    result = []
    for c in sorted(dominant, key=lambda x: x.get("score", 0), reverse=True):
        rgb = c.get("color", {})
        r, g, b = rgb.get("red", 0), rgb.get("green", 0), rgb.get("blue", 0)
        result.append(_rgb_to_name(r, g, b))
    return list(dict.fromkeys(result))  # deduplicate while preserving order


def _rgb_to_name(r: int, g: int, b: int) -> str:
    if r > 200 and g > 200 and b > 200:
        return "white"
    if r < 50 and g < 50 and b < 50:
        return "black"
    if r > 150 and g < 100 and b < 100:
        return "red"
    if r < 100 and g < 100 and b > 150:
        return "blue"
    if r < 100 and g > 100 and b < 100:
        return "green"
    if r > 150 and g > 100 and b < 50:
        return "orange"
    if r > 150 and g > 150 and b < 100:
        return "yellow"
    if r > 150 and g < 100 and b > 150:
        return "purple"
    if r > 150 and g > 100 and b > 100:
        return "pink"
    return "neutral"
