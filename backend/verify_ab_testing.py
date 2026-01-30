from app.core.database import SessionLocal
from app.ml.recommender_interface import get_hybrid_recommendations
from app.models.strategy_experiment import StrategyExperiment
from app.models.recommendation_log import RecommendationLog
from app.models.feedback_models import UserFeedback
import random

def verify_ab_loop():
    db = SessionLocal()
    
    # Using User IDs that are less likely to cause collisions but might exist
    # Or just arbitrary IDs - we'll disable foreign keys for the test simulation if needed
    users = [3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010]
    
    print(f"Starting A/B Loop Verification for {len(users)} users...")

    # Clear previous test data for these users
    db.query(StrategyExperiment).filter(StrategyExperiment.user_id.in_(users)).delete(synchronize_session=False)
    db.query(RecommendationLog).filter(RecommendationLog.user_id.in_(users)).delete(synchronize_session=False)
    db.query(UserFeedback).filter(UserFeedback.user_id.in_([str(u) for u in users])).delete(synchronize_session=False)
    db.commit()

    for uid in users:
        # Step A: Get Rec (Assigned to group)
        # Note: get_hybrid_recommendations might fail if user doesn't exist depending on strategy
        # Collaborative filtering needs a real user with ratings.
        # However, for simulation, we'll try to get ANY rec just to trigger the assignment.
        try:
            recs = get_hybrid_recommendations(user_id=uid, top_n=1)
            strategy = recs[0]['strategy']
        except Exception as e:
            # If it fails (e.g. no ratings for CF), we'll skip or use fallback
            print(f"Skipping user {uid} due to error: {e}")
            continue

        print(f"User {uid} assigned to strategy: {strategy}")
        
        # Step B: Record Feedback
        # CF: 80% Like, Content: 20% Like
        prob = 0.8 if strategy == 'collaborative-filtering' else 0.2
        is_liked = 1 if random.random() < prob else 0
        
        fb = UserFeedback(user_id=str(uid), movie_id=123, liked=is_liked)
        db.add(fb)
        db.commit()
    
    print("\nSimulated traffic recorded. Run 'python run_experiment_results.py' to see results.")
    db.close()

if __name__ == "__main__":
    verify_ab_loop()
