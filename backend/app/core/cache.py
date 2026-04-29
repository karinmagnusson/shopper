import json
import logging
from typing import Any

try:
    import redis as redis_lib

    from app.core.config import settings

    _client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
    _client.ping()
    _redis_available = True
except Exception:
    _client = None  # type: ignore[assignment]
    _redis_available = False

logger = logging.getLogger(__name__)

# In-memory fallback when Redis is unavailable
_local_cache: dict[str, Any] = {}


def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    try:
        if _redis_available and _client:
            _client.setex(key, ttl, json.dumps(value))
            return
    except Exception as exc:
        logger.debug("Redis set failed: %s", exc)
    _local_cache[key] = value


def cache_get(key: str) -> Any | None:
    try:
        if _redis_available and _client:
            raw = _client.get(key)
            return json.loads(raw) if raw else None
    except Exception as exc:
        logger.debug("Redis get failed: %s", exc)
    return _local_cache.get(key)


def cache_delete(key: str) -> None:
    try:
        if _redis_available and _client:
            _client.delete(key)
    except Exception as exc:
        logger.debug("Redis delete failed: %s", exc)
    _local_cache.pop(key, None)
