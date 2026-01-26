from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.ml.hybrid_recommender import HybridRecommender
from app.models.feedback_models import UserFeedback
from app.models.base_models import Movie


def get_hybrid_recommendations(
    user_id: int, 
    top_n: int = 10, 
    genres: list[str] | None = None,
    mood: str | None = None,
    time_context: str | None = None
):
    """
    Returns hybrid recommendations in a simple dict format
    for consumption by the AI Agent or other orchestration layers.
    Includes adjustments based on real-time user feedback (Likes).
    """
    session: Session = SessionLocal()
    try:
        hybrid = HybridRecommender(session)
        result = hybrid.recommend(
            user_id=user_id, 
            top_n=top_n, 
            genres=genres,
            mood=mood,
            time_context=time_context
        )

        # Standardize output for agent
        recommendations = []
        for movie in result["recommendations"]:
            recommendations.append({
                "movie_id": movie.get("id"),
                "title": movie.get("title"),
                "explanation": movie.get("explanation", ""),
                "strategy": result.get("strategy")
            })

        # --- FEEDBACK BOOST (Phase 9 Step 3) ---
        # If the user has liked movies, ensure they are prioritized or acknowledged
        positive_feedback = (
            session.query(UserFeedback)
            .filter_by(user_id=str(user_id), liked=1)
            .limit(3)
            .all()
        )
        
        for fb in positive_feedback:
            # Avoid duplicating if already in recommendations
            if any(r["movie_id"] == fb.movie_id for r in recommendations):
                continue
                
            movie_obj = session.query(Movie).get(fb.movie_id)
            if movie_obj:
                recommendations.insert(0, {
                    "movie_id": fb.movie_id,
                    "title": movie_obj.title,
                    "explanation": "Highly recommended based on your recent 'Like'.",
                    "strategy": "feedback-boost"
                })

        return recommendations[:top_n]

    finally:
        session.close()
