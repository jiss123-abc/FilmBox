from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base

class UserStrategyStats(Base):
    __tablename__ = "user_strategy_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    strategy = Column(String, nullable=False)
    total_used = Column(Integer, default=0)
    positive_feedback = Column(Integer, default=0)
    weight = Column(Float, default=1.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
