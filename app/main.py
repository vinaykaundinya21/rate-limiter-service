from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge
from app.algorithms.token_bucket import is_allowed_token_bucket
from app.algorithms.sliding_window import is_allowed_sliding_window
from app.algorithms.fixed_window import is_allowed_fixed_window
from app.redis_client import get_redis, is_redis_available

app = FastAPI(title="Rate Limiter Service")

requests_allowed = Counter(
    "rate_limiter_requests_allowed_total",
    "Total allowed requests",
    ["algorithm", "client_id"]
)
requests_blocked = Counter(
    "rate_limiter_requests_blocked_total",
    "Total blocked requests",
    ["algorithm", "client_id"]
)
redis_health = Gauge(
    "rate_limiter_redis_healthy",
    "Redis health status (1=healthy, 0=down)"
)

Instrumentator().instrument(app).expose(app)

def check_limit(algorithm_fn, client_id, algorithm_name, *args):
    redis = get_redis()
    if redis is None:
        redis_health.set(0)
        requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
        return {
            "client_id": client_id,
            "allowed": True,
            "algorithm": algorithm_name,
            "message": "Request allowed (fail-open: Redis unavailable)",
            "fail_open": True
        }
    redis_health.set(1)
    allowed = algorithm_fn(client_id, *args)
    if allowed:
        requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
        return {"client_id": client_id, "allowed": True, "algorithm": algorithm_name, "message": "Request allowed", "fail_open": False}
    requests_blocked.labels(algorithm=algorithm_name, client_id=client_id).inc()
    raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": algorithm_name, "message": "Too many requests!", "fail_open": False})

@app.get("/")
def root():
    return {"message": "Rate Limiter Service is running"}

@app.get("/health")
def health():
    redis_up = is_redis_available()
    return {
        "status": "healthy",
        "redis": "up" if redis_up else "down (fail-open mode active)",
        "fail_open": not redis_up
    }

@app.post("/check-limit/token-bucket")
def check_token_bucket(client_id: str, capacity: int = 10, refill_rate: float = 1.0):
    return check_limit(is_allowed_token_bucket, client_id, "token_bucket", capacity, refill_rate)

@app.post("/check-limit/sliding-window")
def check_sliding_window(client_id: str, limit: int = 10, window_seconds: int = 60):
    return check_limit(is_allowed_sliding_window, client_id, "sliding_window", limit, window_seconds)

@app.post("/check-limit/fixed-window")
def check_fixed_window(client_id: str, limit: int = 10, window_seconds: int = 60):
    return check_limit(is_allowed_fixed_window, client_id, "fixed_window", limit, window_seconds)
