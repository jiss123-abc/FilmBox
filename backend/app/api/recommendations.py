from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.base_models import Movie
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()

# ----------------------------
# Helper Functions
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_ratings(session: Session):
    from app.models.base_models import Rating
    ratings_data = session.query(Rating).all()
    data = [{"user_id": r.user_id, "movie_id": r.movie_id, "rating": r.rating} for r in ratings_data]
    return pd.DataFrame(data)

def create_user_movie_matrix(ratings_df):
    return ratings_df.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)

def compute_user_similarity(user_movie_matrix):
    similarity = cosine_similarity(user_movie_matrix)
    return pd.DataFrame(similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

def recommend_movies_for_user(user_id, top_n=10):
    session = next(get_db())
    ratings_df = load_ratings(session)
    if ratings_df.empty:
        return []

    user_movie_matrix = create_user_movie_matrix(ratings_df)
    if user_id not in user_movie_matrix.index:
        return []

    similarity_df = compute_user_similarity(user_movie_matrix)
    sim_scores = similarity_df[user_id]
    weighted_ratings = user_movie_matrix.T.dot(sim_scores) / sim_scores.sum()
    rated_movies = user_movie_matrix.loc[user_id]
    weighted_ratings = weighted_ratings[rated_movies == 0]
    top_movies_ids = weighted_ratings.sort_values(ascending=False).head(top_n).index.tolist()

    # Get movie details from DB
    movies = session.query(Movie).filter(Movie.id.in_(top_movies_ids)).all()
    return [{"id": m.id, "title": m.title, "release_year": m.release_year} for m in movies]

@router.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, top_n: int = 10):
    recommended_movies = recommend_movies_for_user(user_id, top_n)
    if not recommended_movies:
        raise HTTPException(status_code=404, detail="No recommendations available for this user.")
    return {"user_id": user_id, "recommended_movies": recommended_movies}
