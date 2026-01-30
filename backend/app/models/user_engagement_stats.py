from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base

class UserEngagementStats(Base):
    __tablename__ = "user_engagement_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    total_recommendations = Column(Integer, default=0)
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    engagement_score = Column(Float, default=0.0)
