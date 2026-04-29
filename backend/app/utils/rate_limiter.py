import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window = window_seconds
        self._calls: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, int]:
        now = time.time()
        window_start = now - self.window
        calls = [t for t in self._calls[key] if t > window_start]
        self._calls[key] = calls
        if len(calls) >= self.max_calls:
            return False, self.max_calls - len(calls)
        self._calls[key].append(now)
        return True, self.max_calls - len(self._calls[key])


# 10 auth attempts per 15 minutes per IP
auth_limiter = RateLimiter(max_calls=10, window_seconds=900)
# 1000 Pinterest API calls per hour
pinterest_limiter = RateLimiter(max_calls=1000, window_seconds=3600)
