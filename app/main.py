from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge
from sqlalchemy.orm import Session
from app.algorithms.token_bucket import is_allowed_token_bucket
from app.algorithms.sliding_window import is_allowed_sliding_window
from app.algorithms.fixed_window import is_allowed_fixed_window
from app.redis_client import get_redis, is_redis_available
from app.db.database import get_db, engine, Base, SessionLocal
from app.models.request_log import RequestLog
from app.models.user import User
from app.models.api_key import APIKey
from app.auth.routes import router as auth_router
from app.auth.rule_routes import router as rule_router
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RateLimiter Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rule_router)

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

def get_tenant(api_key: str, db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()
    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key

def log_request(user_id: int, client_id: str, algorithm: str, allowed: bool):
    try:
        db = SessionLocal()
        from app.models.request_log import RequestLog
        log = RequestLog(
            user_id=user_id,
            client_id=client_id,
            algorithm=algorithm,
            allowed=allowed
        )
        db.add(log)
        db.commit()
        db.close()
    except Exception:
        pass

def check_limit(algorithm_fn, client_id, algorithm_name, tenant, *args):
    redis = get_redis()
    if redis is None:
        redis_health.set(0)
        requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
        log_request(tenant.user_id, client_id, algorithm_name, True)
        return {
            "client_id": client_id,
            "allowed": True,
            "algorithm": algorithm_name,
            "message": "Request allowed (fail-open: Redis unavailable)",
            "fail_open": True
        }
    redis_health.set(1)
    allowed = algorithm_fn(client_id, *args)
    log_request(tenant.user_id, client_id, algorithm_name, allowed)
    if allowed:
        requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
        return {"client_id": client_id, "allowed": True, "algorithm": algorithm_name, "message": "Request allowed", "fail_open": False}
    requests_blocked.labels(algorithm=algorithm_name, client_id=client_id).inc()
    raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": algorithm_name, "message": "Too many requests!", "fail_open": False})

# def check_limit(algorithm_fn, client_id, algorithm_name, *args):
#     redis = get_redis()
#     if redis is None:
#         redis_health.set(0)
#         requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
#         return {
#             "client_id": client_id,
#             "allowed": True,
#             "algorithm": algorithm_name,
#             "message": "Request allowed (fail-open: Redis unavailable)",
#             "fail_open": True
#         }
#     redis_health.set(1)
#     allowed = algorithm_fn(client_id, *args)
#     if allowed:
#         requests_allowed.labels(algorithm=algorithm_name, client_id=client_id).inc()
#         return {"client_id": client_id, "allowed": True, "algorithm": algorithm_name, "message": "Request allowed", "fail_open": False}
#     requests_blocked.labels(algorithm=algorithm_name, client_id=client_id).inc()
#     raise HTTPException(status_code=429, detail={"client_id": client_id, "allowed": False, "algorithm": algorithm_name, "message": "Too many requests!", "fail_open": False})

@app.get("/")
def root():
    return {"message": "RateLimiter Pro is running"}

@app.get("/health")
def health():
    redis_up = is_redis_available()
    return {
        "status": "healthy",
        "redis": "up" if redis_up else "down (fail-open mode active)",
        "fail_open": not redis_up
    }

@app.post("/check-limit/token-bucket")
def check_token_bucket(
    client_id: str,
    capacity: int = 10,
    refill_rate: float = 1.0,
    tenant: APIKey = Depends(get_tenant)
):
    scoped_client = f"{tenant.user_id}:{client_id}"
    return check_limit(is_allowed_token_bucket, scoped_client, "token_bucket", tenant, capacity, refill_rate)

@app.post("/check-limit/sliding-window")
def check_sliding_window(
    client_id: str,
    limit: int = 10,
    window_seconds: int = 60,
    tenant: APIKey = Depends(get_tenant)
):
    scoped_client = f"{tenant.user_id}:{client_id}"
    return check_limit(is_allowed_sliding_window, scoped_client, "sliding_window", tenant, limit, window_seconds)

@app.post("/check-limit/fixed-window")
def check_fixed_window(
    client_id: str,
    limit: int = 10,
    window_seconds: int = 60,
    tenant: APIKey = Depends(get_tenant)
):
    scoped_client = f"{tenant.user_id}:{client_id}"
    return check_limit(is_allowed_fixed_window, scoped_client, "fixed_window", tenant, limit, window_seconds)


@app.get("/analytics")
def get_analytics(api_key: str, db: Session = Depends(get_db)):
    from app.models.request_log import RequestLog
    tenant = get_tenant(api_key=api_key, db=db)
    logs = db.query(RequestLog).filter(
        RequestLog.user_id == tenant.user_id
    ).order_by(RequestLog.created_at.desc()).limit(100).all()

    total = len(logs)
    allowed = sum(1 for l in logs if l.allowed)
    blocked = total - allowed

    return {
        "total_requests": total,
        "allowed": allowed,
        "blocked": blocked,
        "block_rate": round(blocked / total * 100, 1) if total > 0 else 0,
        "recent_logs": [
            {
                "client_id": l.client_id,
                "algorithm": l.algorithm,
                "allowed": l.allowed,
                "timestamp": l.created_at
            } for l in logs[:10]
        ]
    }