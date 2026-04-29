"""Fashion analysis service using Google Vision API and PIL."""

import io
import logging
import math
from dataclasses import dataclass, field
from typing import Any

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# Mapping Vision API labels → internal fashion category
FASHION_CATEGORY_MAP: dict[str, str] = {
    "top": "tops",
    "shirt": "tops",
    "blouse": "tops",
    "t-shirt": "tops",
    "sweater": "tops",
    "hoodie": "tops",
    "jacket": "outerwear",
    "coat": "outerwear",
    "blazer": "outerwear",
    "pants": "bottoms",
    "jeans": "bottoms",
    "shorts": "bottoms",
    "skirt": "bottoms",
    "trousers": "bottoms",
    "leggings": "bottoms",
    "dress": "dresses",
    "gown": "dresses",
    "jumpsuit": "dresses",
    "shoes": "footwear",
    "sneakers": "footwear",
    "boots": "footwear",
    "heels": "footwear",
    "sandals": "footwear",
    "bag": "accessories",
    "handbag": "accessories",
    "purse": "accessories",
    "hat": "accessories",
    "belt": "accessories",
    "scarf": "accessories",
    "jewelry": "accessories",
    "necklace": "accessories",
    "earrings": "accessories",
}

STYLE_KEYWORDS: dict[str, list[str]] = {
    "casual": ["jeans", "sneakers", "hoodie", "t-shirt", "shorts"],
    "formal": ["blazer", "suit", "gown", "heels", "dress shirt"],
    "bohemian": ["floral", "flowy", "maxi", "peasant", "embroidered", "fringe"],
    "vintage": ["retro", "plaid", "corduroy", "mod", "polka dot", "cat-eye"],
    "streetwear": ["sneakers", "oversized", "graphic tee", "joggers", "cap"],
    "athletic": ["leggings", "sports bra", "running shoes", "workout", "gym"],
}


@dataclass
class FashionAnalysis:
    """Structured result of a fashion image analysis."""

    categories: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)
    style_tags: list[str] = field(default_factory=list)
    dominant_style: str = "casual"
    labels: list[str] = field(default_factory=list)
    confidence: float = 0.0
    embedding: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to plain dict for JSON storage."""
        return {
            "categories": self.categories,
            "colors": self.colors,
            "style_tags": self.style_tags,
            "dominant_style": self.dominant_style,
            "labels": self.labels,
            "confidence": self.confidence,
            "embedding": self.embedding,
        }


async def download_image(url: str) -> Image.Image:
    """Download an image from a URL and return a PIL Image.

    Args:
        url: Public image URL.

    Returns:
        PIL Image object.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        response = await client.get(url)
        response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert("RGB")


def extract_dominant_colors(image: Image.Image, num_colors: int = 5) -> list[str]:
    """Extract dominant colors from an image using PIL quantization.

    Args:
        image: PIL Image object (RGB).
        num_colors: Number of dominant colors to extract.

    Returns:
        List of hex color strings e.g. ["#ff0000", "#00ff00"].
    """
    # Resize for speed; quantize into a palette
    small = image.resize((150, 150))
    quantized = small.quantize(colors=num_colors)
    palette_data = quantized.getpalette()
    if not palette_data:
        return []

    # Count pixels per palette entry
    pixel_counts: dict[int, int] = {}
    for pixel in quantized.getdata():
        pixel_counts[pixel] = pixel_counts.get(pixel, 0) + 1

    sorted_indices = sorted(pixel_counts, key=lambda k: pixel_counts[k], reverse=True)
    colors: list[str] = []
    for idx in sorted_indices[:num_colors]:
        r = palette_data[idx * 3]
        g = palette_data[idx * 3 + 1]
        b = palette_data[idx * 3 + 2]
        colors.append(f"#{r:02x}{g:02x}{b:02x}")

    return colors


async def call_vision_api(image_url: str) -> list[dict]:
    """Call Google Vision API label detection on an image URL.

    Args:
        image_url: Publicly accessible image URL.

    Returns:
        List of label annotation dicts from Vision API.
    """
    if not settings.GOOGLE_VISION_API_KEY:
        logger.warning("GOOGLE_VISION_API_KEY not configured, skipping Vision API call")
        return []

    payload = {
        "requests": [
            {
                "image": {"source": {"imageUri": image_url}},
                "features": [
                    {"type": "LABEL_DETECTION", "maxResults": 20},
                    {"type": "IMAGE_PROPERTIES", "maxResults": 5},
                ],
            }
        ]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://vision.googleapis.com/v1/images:annotate",
            params={"key": settings.GOOGLE_VISION_API_KEY},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    responses = data.get("responses", [{}])
    return responses[0].get("labelAnnotations", [])


def classify_style(labels: list[str]) -> tuple[str, list[str]]:
    """Determine dominant style and matching style tags from label strings.

    Args:
        labels: Lower-cased label strings from Vision API.

    Returns:
        Tuple of (dominant_style, matched_style_tags).
    """
    scores: dict[str, int] = {}
    for style, keywords in STYLE_KEYWORDS.items():
        count = sum(1 for kw in keywords if any(kw in lbl for lbl in labels))
        if count:
            scores[style] = count

    if not scores:
        return "casual", []

    dominant = max(scores, key=lambda k: scores[k])
    matched_tags = list(scores.keys())
    return dominant, matched_tags


def _simple_embedding(categories: list[str], colors: list[str], style: str) -> list[float]:
    """Generate a lightweight pseudo-embedding vector.

    The vector is intentionally simple — suitable for cosine-similarity
    matching without requiring a full ML model at MVP stage.

    Returns:
        List of floats (length 14: 7 category bits + 6 style bits + 1 color value).
    """
    all_categories = [
        "tops", "bottoms", "dresses", "outerwear",
        "footwear", "accessories", "other",
    ]
    all_styles = ["casual", "formal", "bohemian", "vintage", "streetwear", "athletic"]

    vec: list[float] = []
    for cat in all_categories:
        vec.append(1.0 if cat in categories else 0.0)
    for sty in all_styles:
        vec.append(1.0 if sty == style else 0.0)
    # Color magnitude (simplified: number of colors / 5)
    vec.append(min(len(colors) / 5.0, 1.0))
    # Normalise
    mag = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / mag for x in vec]


async def analyze_pin_image(image_url: str) -> FashionAnalysis:
    """Run full fashion analysis pipeline on a pin image URL.

    Steps:
      1. Download image for color extraction.
      2. Call Vision API for label detection.
      3. Map labels to fashion categories.
      4. Classify style.
      5. Build embedding vector.

    Args:
        image_url: Public URL of the Pinterest pin image.

    Returns:
        FashionAnalysis dataclass with all analysis results.
    """
    # Run image download and Vision API call concurrently
    import asyncio

    image_task = asyncio.create_task(download_image(image_url))
    vision_task = asyncio.create_task(call_vision_api(image_url))

    image, label_annotations = await asyncio.gather(image_task, vision_task, return_exceptions=True)

    # Handle partial failures gracefully
    colors: list[str] = []
    if isinstance(image, Image.Image):
        colors = extract_dominant_colors(image)
    else:
        logger.warning("Image download failed: %s", image)

    label_annotations = label_annotations if isinstance(label_annotations, list) else []
    raw_labels = [ann.get("description", "").lower() for ann in label_annotations]
    confidence = (
        sum(ann.get("score", 0.0) for ann in label_annotations) / len(label_annotations)
        if label_annotations
        else 0.0
    )

    # Map labels → categories
    categories: list[str] = []
    for label in raw_labels:
        for keyword, category in FASHION_CATEGORY_MAP.items():
            if keyword in label and category not in categories:
                categories.append(category)

    if not categories:
        categories = ["other"]

    dominant_style, style_tags = classify_style(raw_labels)
    embedding = _simple_embedding(categories, colors, dominant_style)

    return FashionAnalysis(
        categories=categories,
        colors=colors,
        style_tags=style_tags,
        dominant_style=dominant_style,
        labels=raw_labels[:15],
        confidence=round(confidence, 4),
        embedding=embedding,
    )
