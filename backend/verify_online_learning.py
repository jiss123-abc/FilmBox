from app.core.database import SessionLocal
from app.ml.recommender_interface import get_hybrid_recommendations
from app.ml.strategy_lookup import get_last_strategy_for_user
from app.ml.strategy_learning import update_strategy_weight, POSITIVE_REWARD, NEGATIVE_PENALTY
from app.models.user_strategy_stats import UserStrategyStats
from app.models.feedback_models import UserFeedback

def verify_learning():
    user_id = 1337
    db = SessionLocal()
    
    # Clean up previous tests
    db.query(UserStrategyStats).filter_by(user_id=user_id).delete()
    db.query(UserFeedback).filter(UserFeedback.user_id == str(user_id)).delete()
    db.commit()

    print(f"Step 1: Get recommendation for User {user_id}")
    get_hybrid_recommendations(user_id=user_id, top_n=1)
    
    # Check stats
    stat = db.query(UserStrategyStats).filter_by(user_id=user_id).first()
    initial_weight = stat.weight
    print(f"Strategy: {stat.strategy}, Initial Weight: {initial_weight}")

    print("\nStep 2: Submit feedback (Automated strategy identification)")
    strategy = get_last_strategy_for_user(user_id)
    print(f"Identified strategy from logs: {strategy}")
    
    # Simulate a LIKE
    update_strategy_weight(user_id, strategy, liked=1)
    
    # Check stats again
    db.refresh(stat)
    print(f"Updated Stats -> Likes: {stat.positive_feedback}, Weight: {stat.weight:.2f}")
    
    expected_weight = initial_weight + POSITIVE_REWARD
    if abs(stat.weight - expected_weight) < 0.01:
        print(f"\n✅ Online Learning Verified: Weight Increased by {POSITIVE_REWARD}!")
    else:
        print(f"\n❌ Verification Failed. Expected {expected_weight}, got {stat.weight}")

    db.close()

    db.close()

if __name__ == "__main__":
    verify_learning()
