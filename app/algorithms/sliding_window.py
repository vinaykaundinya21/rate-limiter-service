import time
from app.redis_client import get_redis

def is_allowed_sliding_window(client_id: str, limit: int, window_seconds: int) -> bool:
    redis = get_redis()
    now = time.time()
    key = f"sliding_window:{client_id}"
    window_start = now - window_seconds

    redis.zremrangebyscore(key, 0, window_start)
    request_count = redis.zcard(key)

    if request_count >= limit:
        return False

    redis.zadd(key, {str(now): now})
    redis.expire(key, window_seconds)
    return True