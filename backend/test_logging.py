from app.core.database import SessionLocal, Base, engine
import app.models.base_models
import app.models.feedback_models
import app.models.analytics_models
from app.ml.hybrid_recommender import HybridRecommender

def test_logging():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    recommender = HybridRecommender(session)
    
    print("Testing recommendation for User 1 (Active User)...")
    recommender.recommend(user_id=1, top_n=5)
    
    print("Testing recommendation for User 999 (New User)...")
    recommender.recommend(user_id=999, top_n=5)
    
    session.close()
    print("Test complete.")

if __name__ == "__main__":
    test_logging()
