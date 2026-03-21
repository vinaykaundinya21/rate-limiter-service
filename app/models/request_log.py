from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    allowed = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())