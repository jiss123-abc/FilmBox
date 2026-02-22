import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.feedback_models import UserFeedback

def check_learning_trend():
    session = SessionLocal()
    print("\n--- Phase 21.4: Learning Validation Check ---\n")

    # Group 1: Users with > 10 interactions
    users_query = (
        session.query(UserFeedback.user_id, func.count(UserFeedback.id).label("count"))
        .group_by(UserFeedback.user_id)
        .having(func.count(UserFeedback.id) > 10)
        .all()
    )
    
    active_users = [u.user_id for u in users_query]
    
    if not active_users:
        print("Not enough user history to prove learning (need users with >10 feedbacks).")
        print("Please run simulations or use the app more.")
        return

    print(f"Analyzing {len(active_users)} active users...")
    
    total_improvement = 0
    improved_users = 0
    
    for user_id in active_users:
        feedbacks = (
            session.query(UserFeedback)
            .filter(UserFeedback.user_id == user_id)
            .order_by(UserFeedback.timestamp.asc())
            .all()
        )
        
        # Split into First 5 vs Last 5
        first_chunk = feedbacks[:5]
        last_chunk = feedbacks[-5:]
        
        avg_early = sum(1 for f in first_chunk if f.liked == 1) / len(first_chunk)
        avg_late = sum(1 for f in last_chunk if f.liked == 1) / len(last_chunk)
        
        improvement = avg_late - avg_early
        total_improvement += improvement
        
        if improvement > 0:
            improved_users += 1
            
        print(f"User {user_id}: Early Avg={avg_early:.2f}, Late Avg={avg_late:.2f} | Diff={improvement:+.2f}")

    avg_lift = total_improvement / len(active_users)
    
    print("-" * 50)
    print(f"Average Lift across all users: {avg_lift:+.2f}")
    
    if avg_lift > 0:
        print("✅ CONCLUSION: The System IS Learning! (Positive Trend)")
    else:
        print("⚠️ CONCLUSION: No clear learning trend detected yet.")
        
    session.close()

if __name__ == "__main__":
    check_learning_trend()
