import logging
import time
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter backed by Redis.

    Each key gets a bucket of `capacity` tokens, refilled at `refill_rate`
    tokens per second.  A single request consumes one token.
    """

    def __init__(
        self,
        capacity: int | None = None,
        refill_window: int | None = None,
    ) -> None:
        self.capacity = capacity or settings.RATE_LIMIT_REQUESTS
        self.refill_window = refill_window or settings.RATE_LIMIT_WINDOW
        self.refill_rate: float = self.capacity / self.refill_window

    async def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check whether the request identified by *key* is within the rate limit.

        Returns (allowed, remaining_tokens).
        """
        redis = await get_redis()
        bucket_key = f"rate_limit:{key}"
        now = time.time()

        async with redis.pipeline(transaction=True) as pipe:
            try:
                await pipe.watch(bucket_key)
                raw = await pipe.hgetall(bucket_key)

                tokens = float(raw.get("tokens", self.capacity))
                last_refill = float(raw.get("last_refill", now))

                # Refill tokens based on elapsed time
                elapsed = now - last_refill
                tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

                if tokens < 1:
                    await pipe.unwatch()
                    return False, 0

                tokens -= 1
                pipe.multi()
                await pipe.hset(bucket_key, mapping={"tokens": tokens, "last_refill": now})
                await pipe.expire(bucket_key, self.refill_window * 2)
                await pipe.execute()
                return True, int(tokens)
            except aioredis.WatchError:
                logger.warning("Rate limiter watch error for key %s; allowing request", key)
                return True, -1

    async def reset(self, key: str) -> None:
        redis = await get_redis()
        await redis.delete(f"rate_limit:{key}")


# Shared singleton used across the application
rate_limiter = TokenBucketRateLimiter()
