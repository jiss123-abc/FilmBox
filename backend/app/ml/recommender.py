from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.base_models import Rating, Movie, Genre, UserSimilarity

class Recommender:
    def __init__(self, session: Session):
        self.session = session

    def recommend(
        self, 
        user_id: str, 
        top_n: int = 10, 
        genre_filter: list[str] | None = None,
        max_runtime: int | None = None,
        min_score: float | None = None,
        language: str | None = None
    ):
        """
        Recommend movies using PRECOMPUTED User-CF SQLite scores.
        Zero memory overhead.
        """
        # 1. Get Top Similar Users
        similarities = (
            self.session.query(UserSimilarity)
            .filter(UserSimilarity.user_id == user_id)
            .order_by(desc(UserSimilarity.similarity_score))
            .limit(15) # Top 15 closest users
            .all()
        )
        
        if not similarities:
            return []
            
        sim_scores_dict = {sim.similar_user_id: sim.similarity_score for sim in similarities}
        similar_user_ids = list(sim_scores_dict.keys())
        
        # 2. Get the movies that these similar users rated highly (>= 4)
        # and that the current user has NOT rated.
        user_rated_movie_ids = {
            r[0] for r in self.session.query(Rating.movie_id).filter(Rating.user_id == user_id).all()
        }
        
        candidate_ratings = (
            self.session.query(Rating)
            .filter(Rating.user_id.in_(similar_user_ids))
            .filter(~Rating.movie_id.in_(user_rated_movie_ids)) # Exclude already watched
            .filter(Rating.rating >= 4) # Only good recommendations
            .all()
        )
        
        if not candidate_ratings:
            return []
            
        # 3. Calculate weighted scores: sum(rating * user_similarity)
        movie_scores = {}
        for r in candidate_ratings:
            weight = sim_scores_dict.get(r.user_id, 0)
            if r.movie_id not in movie_scores:
                movie_scores[r.movie_id] = 0
            movie_scores[r.movie_id] += r.rating * weight
            
        # Sort candidates
        candidate_limit = top_n * 5 if genre_filter else top_n
        top_movies_ids = sorted(movie_scores, key=movie_scores.get, reverse=True)[:candidate_limit]
        
        # Get movie details
        query = self.session.query(Movie).filter(Movie.id.in_(top_movies_ids))
        
        if genre_filter:
            query = query.filter(Movie.genres.any(Genre.name.in_(genre_filter)))

        if max_runtime:
            query = query.filter(Movie.runtime <= max_runtime)
        if min_score:
            query = query.filter(Movie.audience_score >= min_score)
        if language:
            query = query.filter(Movie.language == language)

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
                    "poster_url": m.poster_url,
                    "overview": m.overview,
                    "runtime": m.runtime,
                    "language": m.language,
                    "audience_score": m.audience_score,
                    "genres": [g.name for g in m.genres],
                    "score": float(movie_scores.get(mid, 0)) # Keep the ML score for boosting
                })
            if len(final_list) >= top_n:
                break
                
        return final_list
