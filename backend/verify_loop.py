from app.core.database import SessionLocal, Base, engine
import app.models # Ensure all models are loaded
from app.agents.recommendation_agent import run_recommendation_agent
from app.models.strategy_stats import StrategyStats
from app.models.feedback_models import UserFeedback

def run_loop_test():
    db = SessionLocal()
    try:
        print("--- 🔄 Starting Phase 11.1 Loop Test ---")
        
        # 1. Check Initial State
        strategy_name = "collaborative-filtering"
        stat = db.query(StrategyStats).filter_by(strategy_name=strategy_name).first()
        print(f"Pre-Test: {strategy_name} | Used: {stat.times_used} | Likes: {stat.likes_received} | Weight: {stat.weight:.4f}")
        
        # 2. Trigger Usage (Step 4)
        print(f"\n🚀 Step 1: Serving Recommendation...")
        res = run_recommendation_agent(user_id=1, message="Recommend something similar to 318")
        movie_id = res['recommendations'][0]['movie_id']
        
        # 3. Simulate Like (Step 5 & 6)
        # Note: We simulate the API call logic here
        print(f"❤️ Step 2: Liking Movie {movie_id} via {strategy_name}...")
        
        # This mirrors the feedback_api.py logic
        from app.api.feedback_api import update_strategy_feedback
        update_strategy_feedback(db, strategy_name)
        
        # 4. Check Final State
        db.refresh(stat)
        print(f"\nPost-Test: {strategy_name} | Used: {stat.times_used} | Likes: {stat.likes_received} | Weight: {stat.weight:.4f}")
        
        if stat.weight > 1.0:
            print("\n✅ SUCCESS: Weight increased automatically based on user feedback!")
        else:
            print("\n❌ FAILED: Weight did not increase.")
            
    finally:
        db.close()

if __name__ == "__main__":
    run_loop_test()
