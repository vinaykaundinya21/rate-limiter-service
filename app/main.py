from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter
from app.algorithms.token_bucket import is_allowed_token_bucket
from app.algorithms.sliding_window import is_allowed_sliding_window
from app.algorithms.fixed_window import is_allowed_fixed_window

app = FastAPI(title="Rate Limiter Service")

# Prometheus metrics
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

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {"message": "Rate Limiter Service is running"}

@app.post("/check-limit/token-bucket")
def check_token_bucket(client_id: str, capacity: int = 10, refill_rate: float = 1.0):
    allowed = is_allowed_token_bucket(client_id, capacity, refill_rate)
    if allowed:
        requests_allowed.labels(algorithm="token_bucket", client_id=client_id).inc()
        return {"client_id": client_id, "allowed": True, "algorithm": "token_bucket", "message": "Request allowed"}
    requests_blocked.labels(algorithm="token_bucket", client_id=client_id).inc()
    raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": "token_bucket", "message": "Too many requests!"})

@app.post("/check-limit/sliding-window")
def check_sliding_window(client_id: str, limit: int = 10, window_seconds: int = 60):
    allowed = is_allowed_sliding_window(client_id, limit, window_seconds)
    if allowed:
        requests_allowed.labels(algorithm="sliding_window", client_id=client_id).inc()
        return {"client_id": client_id, "allowed": True, "algorithm": "sliding_window", "message": "Request allowed"}
    requests_blocked.labels(algorithm="sliding_window", client_id=client_id).inc()
    raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": "sliding_window", "message": "Too many requests!"})

@app.post("/check-limit/fixed-window")
def check_fixed_window(client_id: str, limit: int = 10, window_seconds: int = 60):
    allowed = is_allowed_fixed_window(client_id, limit, window_seconds)
    if allowed:
        requests_allowed.labels(algorithm="fixed_window", client_id=client_id).inc()
        return {"client_id": client_id, "allowed": True, "algorithm": "fixed_window", "message": "Request allowed"}
    requests_blocked.labels(algorithm="fixed_window", client_id=client_id).inc()
    raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": "fixed_window", "message": "Too many requests!"})