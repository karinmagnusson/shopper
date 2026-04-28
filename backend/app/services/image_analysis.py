"""Google Cloud Vision API integration for fashion image analysis."""

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.utils.cache import analysis_cache_key, cache_get, cache_set

logger = logging.getLogger(__name__)

VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"

CLOTHING_CATEGORIES = {
    "tops", "shirts", "blouses", "sweaters", "jackets", "coats",
    "dresses", "skirts", "pants", "jeans", "shorts", "shoes",
    "boots", "sneakers", "heels", "bags", "accessories", "hats", "scarves",
}

STYLE_KEYWORDS = {
    "casual", "formal", "bohemian", "minimalist", "streetwear",
    "vintage", "preppy", "athletic", "romantic", "edgy", "classic",
}


class ImageAnalysisService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=20.0)

    async def analyze_image(self, image_url: str) -> dict[str, Any]:
        """
        Analyse a fashion image using Google Vision API.

        Returns a structured dict with: colors, clothing_type, styles,
        detected_brands, labels, and confidence score.
        """
        cache_key = analysis_cache_key(image_url)
        cached = await cache_get(cache_key)
        if cached:
            return cached

        try:
            result = await self._call_vision_api(image_url)
            structured = self._structure_analysis(result)
            await cache_set(cache_key, structured, ttl=86400)
            return structured
        except Exception as exc:
            logger.error("Vision API error for %s: %s", image_url, exc)
            return self._empty_analysis()

    async def _call_vision_api(self, image_url: str) -> dict[str, Any]:
        payload = {
            "requests": [
                {
                    "image": {"source": {"imageUri": image_url}},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 20},
                        {"type": "IMAGE_PROPERTIES", "maxResults": 10},
                        {"type": "LOGO_DETECTION", "maxResults": 5},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 10},
                    ],
                }
            ]
        }
        response = await self._client.post(
            VISION_API_URL,
            params={"key": settings.GOOGLE_VISION_API_KEY},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["responses"][0] if data.get("responses") else {}

    def _structure_analysis(self, raw: dict[str, Any]) -> dict[str, Any]:
        colors = self._extract_colors(raw)
        labels = [a["description"].lower() for a in raw.get("labelAnnotations", [])]
        logos = [l["description"].lower() for l in raw.get("logoAnnotations", [])]

        clothing_type = self._detect_clothing_type(labels)
        styles = self._detect_styles(labels)

        return {
            "colors": colors,
            "clothing_type": clothing_type,
            "styles": styles,
            "detected_brands": logos,
            "labels": labels[:10],
            "confidence": self._compute_confidence(clothing_type, colors, styles),
        }

    def _extract_colors(self, raw: dict[str, Any]) -> list[str]:
        props = raw.get("imagePropertiesAnnotation", {})
        dominant = props.get("dominantColors", {}).get("colors", [])
        named: list[str] = []
        for color_entry in dominant[:5]:
            color = color_entry.get("color", {})
            name = self._rgb_to_name(
                int(color.get("red", 0)),
                int(color.get("green", 0)),
                int(color.get("blue", 0)),
            )
            if name and name not in named:
                named.append(name)
        return named

    @staticmethod
    def _rgb_to_name(r: int, g: int, b: int) -> str:
        """Very simple RGB → colour name mapping."""
        if r > 200 and g > 200 and b > 200:
            return "white"
        if r < 60 and g < 60 and b < 60:
            return "black"
        if r > 150 and g < 100 and b < 100:
            return "red"
        if r < 100 and g < 100 and b > 150:
            return "blue"
        if r < 100 and g > 150 and b < 100:
            return "green"
        if r > 200 and g > 150 and b < 80:
            return "yellow"
        if r > 200 and g > 100 and b < 50:
            return "orange"
        if r > 150 and g < 100 and b > 150:
            return "purple"
        if r > 180 and g > 100 and b > 100:
            return "pink"
        if 80 <= r <= 160 and 60 <= g <= 140 and 40 <= b <= 110:
            return "brown"
        return "neutral"

    @staticmethod
    def _detect_clothing_type(labels: list[str]) -> str | None:
        for label in labels:
            for category in CLOTHING_CATEGORIES:
                if category in label:
                    return category
        return None

    @staticmethod
    def _detect_styles(labels: list[str]) -> list[str]:
        found: list[str] = []
        label_text = " ".join(labels)
        for style in STYLE_KEYWORDS:
            if style in label_text:
                found.append(style)
        return found

    @staticmethod
    def _compute_confidence(
        clothing_type: str | None, colors: list[str], styles: list[str]
    ) -> float:
        score = 0.0
        if clothing_type:
            score += 0.5
        if colors:
            score += min(0.3, len(colors) * 0.1)
        if styles:
            score += min(0.2, len(styles) * 0.1)
        return round(score, 2)

    @staticmethod
    def _empty_analysis() -> dict[str, Any]:
        return {
            "colors": [],
            "clothing_type": None,
            "styles": [],
            "detected_brands": [],
            "labels": [],
            "confidence": 0.0,
        }

    async def analyze_multiple(
        self, image_urls: list[str]
    ) -> list[dict[str, Any]]:
        """Analyse a list of images concurrently."""
        import asyncio
        return await asyncio.gather(*[self.analyze_image(url) for url in image_urls])


image_analysis_service = ImageAnalysisService()
