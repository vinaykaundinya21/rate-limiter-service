import time
from app.redis_client import get_redis

def is_allowed_token_bucket(client_id: str, capacity: int, refill_rate: float) -> bool:
    redis = get_redis()
    now = time.time()
    key = f"token_bucket:{client_id}"

    data = redis.hgetall(key)

    if not data:
        tokens = capacity - 1
        redis.hset(key, mapping={"tokens": tokens, "last_refill": now})
        return True

    tokens = float(data["tokens"])
    last_refill = float(data["last_refill"])

    elapsed = now - last_refill
    refilled = elapsed * refill_rate
    tokens = min(capacity, tokens + refilled)

    if tokens < 1:
        return False

    tokens -= 1
    redis.hset(key, mapping={"tokens": tokens, "last_refill": now})
    return True