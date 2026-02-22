import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.recommendation_log import RecommendationLog
from app.models.feedback_models import UserFeedback
from app.ml.recommendation_logger import log_recommendation_event
from app.scripts.update_schema_phase21 import add_movie_ids_column
import random

def seed_test_data(session: Session):
    print("Seeding test data for evaluation...")
    # Create fake logs and feedback
    strategies = ["content-based", "collaborative-filtering", "popularity-based"]
    
    for i in range(20):
        strat = random.choice(strategies)
        user_id = 99900 + i # Fake users
        
        # Recommendations
        rec_ids = [random.randint(100, 200) for _ in range(5)]
        log_recommendation_event(user_id, strat, 5, movie_ids=rec_ids)
        
        # Simulate feedback (Hit)
        if random.random() > 0.5:
            # User likes one of the recommended movies
            liked_movie = random.choice(rec_ids)
            feedback = UserFeedback(
                user_id=str(user_id),
                movie_id=liked_movie,
                liked=1,
                strategy=strat
            )
            session.add(feedback)
    
    session.commit()
    print("Seeding complete.")

def calculate_offline_metrics():
    session = SessionLocal()
    
    # Ensure schema is ready
    add_movie_ids_column()
    
    # Check if we have data, if not seed some
    count = session.query(RecommendationLog).filter(RecommendationLog.movie_ids != None).count()
    if count < 5:
        seed_test_data(session)

    print("\n--- Offline Evaluation Metrics (Phase 21.1) ---\n")
    
    # 1. Fetch all logs with movie_ids
    logs = session.query(RecommendationLog).filter(RecommendationLog.movie_ids != "").all()
    
    strategy_stats = {} 
    # { "strategy_name": {"recommendations": 0, "hits": 0, "feedbacks": 0} }

    # Helper to track stats
    for log in logs:
        strat = log.strategy
        if strat not in strategy_stats:
            strategy_stats[strat] = {"recommendations": 0, "hits": 0, "total_recs_count": 0}
        
        strategy_stats[strat]["recommendations"] += 1 # One batch
        strategy_stats[strat]["total_recs_count"] += log.num_recommendations
        
        # Parse IDs
        try:
            rec_movie_ids = set(map(str, log.movie_ids.split(",")))
        except:
            continue
            
        # Check for hits in UserFeedback
        # We look for ANY feedback for this user and these movies
        # This is a loose validtion: if user liked movie X *after* we recommended it.
        # Ideally check timestamps, but for now we check existence.
        
        hits = (
            session.query(UserFeedback)
            .filter(UserFeedback.user_id == log.user_id)
            .filter(UserFeedback.movie_id.in_(rec_movie_ids))
            .filter(UserFeedback.liked == 1)
            .count()
        )
        
        if hits > 0:
            strategy_stats[strat]["hits"] += hits

    # Print Report
    print(f"{'Strategy':<25} | {'Batches':<8} | {'Precision@K':<12} | {'Hit Rate':<10}")
    print("-" * 65)
    
    for strat, data in strategy_stats.items():
        batches = data["recommendations"]
        recs = data["total_recs_count"]
        hits = data["hits"]
        
        # Precision: Proportion of recommended items that were hits
        precision = (hits / recs * 100) if recs > 0 else 0.0
        
        # Hit Rate: Proportion of batches that had at least one hit
        # (Requires tracking hits per batch, which we did in the loop partially, let's refine)
        # Note: The current 'hits' counts total liked items. 
        # Ideally, we need 'batches_with_hits'.
        # Re-calc for proper Hit Rate if needed, but for now we'll use a simplified HIT_RATE estimation or just Precision.
        # Actually, let's validly count batches_with_hits.
        pass
        
    # Re-loop to count batches_with_hits correctly
    strategy_metrics = {}
    
    for log in logs:
        strat = log.strategy
        if strat not in strategy_metrics:
            strategy_metrics[strat] = {"batches": 0, "hits": 0, "batches_with_hit": 0, "total_items": 0}
            
        strategy_metrics[strat]["batches"] += 1
        strategy_metrics[strat]["total_items"] += log.num_recommendations
        
        try:
            rec_movie_ids = set(map(str, log.movie_ids.split(",")))
            # Check hits
            batch_hits = (
                session.query(UserFeedback)
                .filter(UserFeedback.user_id == log.user_id)
                .filter(UserFeedback.movie_id.in_(rec_movie_ids))
                .filter(UserFeedback.liked == 1)
                .count()
            )
            
            strategy_metrics[strat]["hits"] += batch_hits
            if batch_hits > 0:
                strategy_metrics[strat]["batches_with_hit"] += 1
        except:
             pass

    for strat, m in strategy_metrics.items():
        precision = (m["hits"] / m["total_items"] * 100) if m["total_items"] > 0 else 0.0
        hit_rate = (m["batches_with_hit"] / m["batches"] * 100) if m["batches"] > 0 else 0.0
        
        print(f"{strat:<25} | {m['batches']:<8} | {precision:6.2f}%      | {hit_rate:6.2f}%")
        
    session.close()

if __name__ == "__main__":
    calculate_offline_metrics()
