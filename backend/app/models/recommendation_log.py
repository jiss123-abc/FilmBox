from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    strategy = Column(String, nullable=False)
    experiment_group = Column(String, nullable=True)  # New for Phase 14
    num_recommendations = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
