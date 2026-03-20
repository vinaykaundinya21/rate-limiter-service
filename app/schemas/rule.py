from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RuleCreate(BaseModel):
    client_id_pattern: str
    algorithm: str = "token_bucket"
    capacity: int = 10
    refill_rate: float = 1.0
    limit: int = 10
    window_seconds: int = 60

class RuleResponse(BaseModel):
    id: int
    client_id_pattern: str
    algorithm: str
    capacity: int
    refill_rate: float
    limit: int
    window_seconds: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True