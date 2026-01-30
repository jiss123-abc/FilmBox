from app.core.database import SessionLocal
from app.analytics.strategy_metrics import get_strategy_metrics
from app.models.feedback_models import UserFeedback
from app.ml.strategy_lookup import get_last_strategy_for_user

def verify_leaderboard():
    db = SessionLocal()
    
    print("--- Phase 15.1: Global Strategy Leaderboard Verification ---")
    
    # 1. Backfill Strategy for User 42 if missing (since we just added the column)
    target_user = "42"
    strategy = get_last_strategy_for_user(int(target_user))
    
    if strategy:
        feedbacks = db.query(UserFeedback).filter(UserFeedback.user_id == target_user, UserFeedback.strategy == None).all()
        if feedbacks:
            print(f"Backfilling {len(feedbacks)} feedback records for User {target_user} with strategy: {strategy}")
            for f in feedbacks:
                f.strategy = strategy
            db.commit()

    # 2. Run Leaderboard Analytics
    results = get_strategy_metrics(db)
    
    print("\nGlobal Leaderboard:")
    print(f"{'Strategy':<25} | {'Impressions':<12} | {'Likes':<8} | {'CTR':<8}")
    print("-" * 65)
    
    for row in results:
        print(f"{row.strategy or 'Unknown':<25} | {row.impressions:<12} | {row.likes:<8} | {row.ctr if row.ctr is not None else 0:.3f}")

    db.close()

if __name__ == "__main__":
    verify_leaderboard()
