from app.core.database import SessionLocal
from app.agents.recommendation_agent import run_recommendation_agent
from app.api.feedback_api import update_user_strategy_feedback, update_strategy_feedback
from app.models.user_strategy_stats import UserStrategyStats
from app.models.strategy_stats import StrategyStats

def test_personalization():
    db = SessionLocal()
    try:
        # User 42 will like Collaborative Filtering
        # User 100 will like Content-Based
        
        users = [
            {"id": 42, "pref": "collaborative-filtering"},
            {"id": 100, "pref": "content-based"}
        ]
        
        for user in users:
            uid = user["id"]
            strategy = user["pref"]
            
            print(f"\n👤 Testing User {uid} (Target Preference: {strategy})")
            
            # 1. Trigger Usage
            print(f" - Serving recommendation...")
            run_recommendation_agent(user_id=uid, message="Give me a movie recommendation")
            
            # 2. Provide Feedback (Reward the target strategy)
            print(f" - Simulating 'Like' for {strategy}...")
            update_user_strategy_feedback(db, uid, strategy)
            update_strategy_feedback(db, strategy)
            
            # 3. Check Weights
            row = db.query(UserStrategyStats).filter_by(user_id=uid, strategy_name=strategy).first()
            print(f" ✅ User {uid} weight for {strategy}: {row.weight:.4f}")

        print("\n--- 🏁 Verification SQL Snapshot ---")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_personalization()
