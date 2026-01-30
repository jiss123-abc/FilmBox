from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    strategy = Column(String, nullable=False)
    experiment_group = Column(String, nullable=True)  # New for Phase 14
    num_recommendations = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
