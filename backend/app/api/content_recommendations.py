from fastapi import APIRouter, HTTPException
from app.core.database import SessionLocal
from app.ml.content_recommender import ContentRecommender

router = APIRouter()

@router.get("/content-recommendations/{movie_id}")
def get_similar_movies(movie_id: int, top_n: int = 10):
    session = SessionLocal()
    try:
        recommender = ContentRecommender(session)
        results = recommender.recommend_similar_movies(movie_id, top_n)
        if not results:
            raise HTTPException(status_code=404, detail="No similar movies found")
        return {
            "movie_id": movie_id,
            "recommended_movies": results
        }
    finally:
        session.close()
