import json
import logging
from typing import Any, TypeVar

import redis.asyncio as aioredis

from app.utils.rate_limiter import get_redis

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_TTL = 3600  # 1 hour


async def cache_get(key: str) -> Any | None:
    """Retrieve a cached JSON value. Returns None on miss or error."""
    try:
        redis: aioredis.Redis = await get_redis()
        raw = await redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache get failed for key %s: %s", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
    """Store a JSON-serialisable value. Returns True on success."""
    try:
        redis: aioredis.Redis = await get_redis()
        await redis.set(key, json.dumps(value), ex=ttl)
        return True
    except Exception as exc:
        logger.warning("Cache set failed for key %s: %s", key, exc)
        return False


async def cache_delete(key: str) -> bool:
    """Delete a cached value. Returns True on success."""
    try:
        redis: aioredis.Redis = await get_redis()
        await redis.delete(key)
        return True
    except Exception as exc:
        logger.warning("Cache delete failed for key %s: %s", key, exc)
        return False


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Returns number of deleted keys."""
    try:
        redis: aioredis.Redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            return await redis.delete(*keys)
        return 0
    except Exception as exc:
        logger.warning("Cache delete_pattern failed for pattern %s: %s", pattern, exc)
        return 0


def board_cache_key(user_id: str) -> str:
    return f"boards:{user_id}"


def pins_cache_key(board_id: str) -> str:
    return f"pins:{board_id}"


def recommendations_cache_key(user_id: str, filters_hash: str) -> str:
    return f"recommendations:{user_id}:{filters_hash}"


def analysis_cache_key(pin_id: str) -> str:
    return f"analysis:{pin_id}"
