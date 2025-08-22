import time
from typing import Optional

import redis

from app.core.config import settings

_client: Optional[redis.Redis] = None
_memory_store: dict[str, tuple[int, int]] = {}


def get_client() -> redis.Redis:
    global _client
    if _client is None:
        if not settings.REDIS_URL:
            raise RuntimeError("Redis URL not configured")
        _client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


def is_allowed(key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Return (allowed, remaining_seconds) using simple fixed-window counter.

    Uses Redis if configured, otherwise a best-effort in-memory store.
    """
    now = int(time.time())
    if settings.REDIS_URL:
        try:
            r = get_client()
            window_key = f"rl:{key}:{now // window_seconds}"
            pipe = r.pipeline()
            pipe.incr(window_key, 1)
            pipe.expire(window_key, window_seconds)
            count, _ = pipe.execute()
            if int(count) > limit:
                remaining = window_seconds - (now % window_seconds)
                return False, remaining
            return True, 0
        except Exception:
            # If Redis is unreachable or errors, fall back to in-memory logic below.
            pass

    # In-memory fallback (per-process, resets on restart)
    win = now // window_seconds
    local_key = f"{key}:{win}"
    count, first_ts = _memory_store.get(local_key, (0, now))
    count += 1
    _memory_store[local_key] = (count, first_ts)
    if count > limit:
        remaining = window_seconds - (now - first_ts)
        if remaining < 0:
            remaining = 0
        return False, remaining
    return True, 0
