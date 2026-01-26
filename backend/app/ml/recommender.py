import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models.base_models import Rating, Movie, Genre

class Recommender:
    def __init__(self, session: Session):
        self.session = session

    def load_ratings(self):
        ratings_data = self.session.query(Rating).all()
        data = [{"user_id": r.user_id, "movie_id": r.movie_id, "rating": r.rating} for r in ratings_data]
        return pd.DataFrame(data)

    def create_user_movie_matrix(self, ratings_df):
        return ratings_df.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)

    def compute_user_similarity(self, user_movie_matrix):
        similarity = cosine_similarity(user_movie_matrix)
        return pd.DataFrame(similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    def recommend(self, user_id: str, top_n: int = 10, genre_filter: list[str] | None = None):
        ratings_df = self.load_ratings()
        if ratings_df.empty:
            return []
            
        user_movie_matrix = self.create_user_movie_matrix(ratings_df)
        if user_id not in user_movie_matrix.index:
            return []

        similarity_df = self.compute_user_similarity(user_movie_matrix)
        sim_scores = similarity_df[user_id]
        
        # Weighted sum of ratings from similar users
        weighted_ratings = user_movie_matrix.T.dot(sim_scores) / sim_scores.sum()
        
        # Remove movies already rated by the user
        rated_movies = user_movie_matrix.loc[user_id]
        weighted_ratings = weighted_ratings[rated_movies == 0]

        # Get candidates (get more than needed to allow for genre filtering)
        # If no filter, just take top_n. If filter, take a larger buffer.
        candidate_limit = top_n * 5 if genre_filter else top_n
        top_movies_ids = weighted_ratings.sort_values(ascending=False).head(candidate_limit).index.tolist()
        
        # Get movie details
        query = self.session.query(Movie).filter(Movie.id.in_(top_movies_ids))
        
        if genre_filter:
            query = query.filter(Movie.genres.any(Genre.name.in_(genre_filter)))

        movies = query.all()
        
        # Re-sort because SQL in_ doesn't guarantee order, and take top_n
        movie_dict = {m.id: m for m in movies}
        final_list = []
        for mid in top_movies_ids:
            if mid in movie_dict:
                m = movie_dict[mid]
                final_list.append({
                    "id": m.id, 
                    "title": m.title, 
                    "release_year": m.release_year,
                    "genres": [g.name for g in m.genres],
                    "score": float(weighted_ratings[mid]) # Keep the ML score for boosting
                })
            if len(final_list) >= top_n:
                break
                
        return final_list
