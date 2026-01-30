from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from datetime import datetime
from app.core.database import Base

class UserGenrePreferences(Base):
    __tablename__ = "user_genre_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True) # String user_id
    genre = Column(String, nullable=False)
    weight = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'genre', name='_user_genre_uc'),
    )
