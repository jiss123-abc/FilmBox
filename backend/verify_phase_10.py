from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
import app.models.base_models
import app.models.feedback_models
import app.models.analytics_models
from app.agents.recommendation_agent import run_recommendation_agent
from app.models.feedback_models import UserFeedback
from app.models.analytics_models import RecommendationLog

def manual_verification():
    # 1. Initialize DB
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    user_id = 42  # Test user
    test_message = "I want a space adventure movie"
    
    print(f"🚀 Step 1: Requesting Agent Recommendation for user {user_id}...")
    # This calls HybridRecommender internally which logs to RecommendationLog
    response = run_recommendation_agent(user_id=user_id, message=test_message)
    
    # Extract a movie ID from the recommendations to "like"
    recommended_movies = response.get("recommendations", [])
    if not recommended_movies:
        print("❌ No movies recommended.")
        return
    
    target_movie = recommended_movies[0]
    movie_id = target_movie.get("movie_id")
    if not movie_id:
        print(f"❌ Could not find movie_id in {target_movie}")
        return
    print(f"🎬 Step 2: Liking recommended movie {movie_id} ('{target_movie.get('title')}')")
    
    # Simulate feedback submission (as per feedback_api logic)
    feedback = UserFeedback(
        user_id=str(user_id),
        movie_id=movie_id,
        liked=1
    )
    session.add(feedback)
    session.commit()
    
    print("\n✅ Verification Queries:")
    
    print("\n🔍 Recent User Feedback (Limit 5):")
    feedbacks = session.query(UserFeedback).order_by(UserFeedback.id.desc()).limit(5).all()
    print(f"{'ID':<5} | {'User ID':<10} | {'Movie ID':<10} | {'Liked':<5}")
    for fb in feedbacks:
        print(f"{fb.id:<5} | {fb.user_id:<10} | {fb.movie_id:<10} | {fb.liked:<5}")
        
    print("\n🔍 Recent Recommendation Logs (Limit 5):")
    logs = session.query(RecommendationLog).order_by(RecommendationLog.id.desc()).limit(5).all()
    print(f"{'ID':<5} | {'User ID':<10} | {'Strategy':<20}")
    for log in logs:
        print(f"{log.id:<5} | {log.user_id:<10} | {log.strategy:<20}")

    session.close()

if __name__ == "__main__":
    manual_verification()
