from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class StrategyStats(Base):
    __tablename__ = "strategy_stats"

    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String, unique=True, nullable=False)
    times_used = Column(Integer, default=0)
    likes_received = Column(Integer, default=0)
    weight = Column(Float, default=1.0)
