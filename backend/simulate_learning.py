import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.feedback_models import UserFeedback
import random
from datetime import datetime, timedelta

def simulate_learning_curve():
    session = SessionLocal()
    print("Simulating learning curve for User 42...")
    
    user_id = "42" # Our favorite test user
    
    # 1. Early stage (Random/Low Performance)
    # Simulate 10 interactions with low hit rate (20%)
    base_time = datetime.utcnow() - timedelta(days=10)
    
    for i in range(10):
        liked = 1 if random.random() < 0.2 else 0
        fb = UserFeedback(
            user_id=user_id,
            movie_id=random.randint(1000, 2000),
            liked=liked,
            timestamp=base_time + timedelta(hours=i)
        )
        session.add(fb)
        
    # 2. Late stage (Learned/High Performance)
    # Simulate 10 interactions with high hit rate (80%)
    base_time = datetime.utcnow()
    
    for i in range(10):
        liked = 1 if random.random() < 0.8 else 0
        fb = UserFeedback(
            user_id=user_id,
            movie_id=random.randint(2001, 3000),
            liked=liked,
            timestamp=base_time + timedelta(hours=i)
        )
        session.add(fb)
        
    session.commit()
    print("Simulation complete. Added 20 feedback points.")
    session.close()

if __name__ == "__main__":
    simulate_learning_curve()
