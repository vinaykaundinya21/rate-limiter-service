# Rate Limiter Service

A production-grade distributed rate limiting microservice built with FastAPI, Redis, and Docker.
Supports 3 algorithms with a clean REST API — plug it into any application to control traffic.

![CI Pipeline](https://github.com/vinaykaundinya21/rate-limiter-service/actions/workflows/ci.yml/badge.svg)

## Algorithms

| Algorithm | How it works | Best for |
|---|---|---|
| Token Bucket | Tokens refill over time, requests consume tokens | APIs with burst tolerance |
| Sliding Window | Tracks requests in a rolling time window | Strict per-user rate limiting |
| Fixed Window | Counts requests in fixed time slots | Simple quota enforcement |

## Tech Stack

- **FastAPI** — REST API framework
- **Redis** — Distributed state store (works across multiple instances)
- **Docker + Docker Compose** — Containerized deployment
- **Pytest** — 9 unit tests with 100% pass rate
- **GitHub Actions** — CI/CD pipeline on every push

## Run Locally

**With Docker (recommended):**
```bash
docker compose up --build
```

**Without Docker:**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints
```
POST /check-limit/token-bucket?client_id=user1&capacity=10&refill_rate=1.0
POST /check-limit/sliding-window?client_id=user1&limit=10&window_seconds=60
POST /check-limit/fixed-window?client_id=user1&limit=10&window_seconds=60
```

## Example Response

**Allowed (200):**
```json
{
  "client_id": "user1",
  "allowed": true,
  "algorithm": "token_bucket",
  "message": "Request allowed"
}
```

**Blocked (429):**
```json
{
  "client_id": "user1",
  "allowed": false,
  "algorithm": "token_bucket",
  "message": "Too many requests!"
}
```

## Run Tests
```bash
python -m pytest tests/ -v
```

## Why This Project

Rate limiting is core infrastructure at every scaled tech company — Razorpay uses it to
protect payment APIs, Swiggy uses it to prevent order spam, Amazon uses it across
internal microservices. This project implements the same patterns from scratch with a
focus on distributed correctness — state is stored in Redis so the limiter works across
multiple service instances, not just in-memory.

## Architecture
```
Client Request → FastAPI → Algorithm (Token Bucket / Sliding Window / Fixed Window)
                                          ↓
                                    Redis (shared state)
                                          ↓
                              Allow (200) or Block (429)
```
```

Hit **Cmd + S**. Then:
```
git add .
git commit -m "docs: add production grade README"
git push origin main