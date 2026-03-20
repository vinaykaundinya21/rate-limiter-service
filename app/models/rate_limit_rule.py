from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class RateLimitRule(Base):
    __tablename__ = "rate_limit_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id_pattern = Column(String, nullable=False)
    algorithm = Column(String, default="token_bucket")
    capacity = Column(Integer, default=10)
    refill_rate = Column(Float, default=1.0)
    limit = Column(Integer, default=10)
    window_seconds = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())