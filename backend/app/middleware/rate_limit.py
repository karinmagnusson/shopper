"""Redis-backed rate-limiting middleware."""

import logging
import time
from typing import Awaitable, Callable

import redis.asyncio as aioredis
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis:
    """Return a module-level shared Redis async client (lazy init)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter that uses Redis INCR + EXPIRE.

    Limits each client IP to ``requests_per_minute`` requests per 60-second
    window.  When Redis is unavailable the middleware degrades gracefully and
    allows the request through.
    """

    def __init__(self, app, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Check rate limit before forwarding to the next handler."""
        # Health checks are excluded from rate limiting
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{int(time.time()) // 60}"

        try:
            redis = _get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 60)

            if count > self.requests_per_minute:
                logger.warning("Rate limit exceeded for IP %s (count=%d)", client_ip, count)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down."},
                    headers={"Retry-After": "60"},
                )
        except Exception:
            # Redis unavailable – fail open
            logger.debug("Rate limiter Redis error, allowing request through", exc_info=True)

        return await call_next(request)
