from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base_models import Base

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False) # Changed to String to match users.id
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    rating = Column(Float, nullable=True)  # Optional explicit rating
    liked = Column(Integer, nullable=True)  # 1 = liked, 0 = disliked
    strategy = Column(String, nullable=True) # New for Phase 15: Denormalized for fast analytics
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    movie = relationship("Movie", back_populates="feedbacks")
