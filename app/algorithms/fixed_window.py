import time
from app.redis_client import get_redis

def is_allowed_fixed_window(client_id: str, limit: int, window_seconds: int) -> bool:
    redis = get_redis()
    window = int(time.time() // window_seconds)
    key = f"fixed_window:{client_id}:{window}"

    count = redis.incr(key)

    if count == 1:
        redis.expire(key, window_seconds)

    if count > limit:
        return False

    return True