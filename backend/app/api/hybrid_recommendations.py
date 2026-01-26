from fastapi import APIRouter, HTTPException
from app.core.database import SessionLocal
from app.ml.hybrid_recommender import HybridRecommender

router = APIRouter()

@router.get("/hybrid-recommendations/{user_id}")
def hybrid_recommendations(user_id: int, top_n: int = 10):
    session = SessionLocal()
    try:
        recommender = HybridRecommender(session)
        result = recommender.recommend(user_id, top_n)

        if not result["recommendations"]:
            raise HTTPException(
                status_code=404,
                detail="No recommendations available"
            )

        return {
            "user_id": user_id,
            "strategy": result["strategy"],
            "reason": result["reason"],
            "recommended_movies": result["recommendations"]
        }
    finally:
        session.close()
