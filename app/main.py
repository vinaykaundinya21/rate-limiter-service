from fastapi import FastAPI, HTTPException
from app.algorithms.token_bucket import is_allowed_token_bucket

app = FastAPI(title="Rate Limiter Service")

@app.get("/")
def root():
    return {"message": "Rate Limiter Service is running"}

@app.post("/check-limit/token-bucket")
def check_token_bucket(client_id: str, capacity: int = 10, refill_rate: float = 1.0):
    allowed = is_allowed_token_bucket(client_id, capacity, refill_rate)
    
    if allowed:
        return {
            "client_id": client_id,
            "allowed": True,
            "message": "Request allowed"
        }
    else:
        raise HTTPException(
            status_code=429,
            detail={
                "client_id": client_id,
                "allowed": False,
                "message": "Too many requests. Slow down!"
            }
        )

# Hit **Cmd + S** to save.

# Now let's run the server! Go to terminal and run:
# ```
# uvicorn app.main:app --reload
# ```

# You should see something like:
# ```
# INFO: Uvicorn running on http://127.0.0.1:8000