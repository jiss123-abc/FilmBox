import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.base_models import Movie, Genre, MovieSimilarity

class ContentRecommender:
    def __init__(self, session: Session):
        self.session = session


    def recommend_similar_movies(
        self, 
        movie_id: int, 
        top_n: int = 10, 
        genre_filter: list[str] | None = None,
        max_runtime: int | None = None,
        min_score: float | None = None,
        language: str | None = None
    ):
        """
        Recommend movies similar to a given movie using PRECOMPUTED SQLite scores.
        Zero memory overhead.
        """
        # Fetch precomputed similarities
        candidate_count = top_n * 10 if genre_filter else top_n + 5
        
        similarities = (
            self.session.query(MovieSimilarity)
            .filter(MovieSimilarity.movie_id == movie_id)
            .order_by(desc(MovieSimilarity.similarity_score))
            .limit(candidate_count)
            .all()
        )
        
        if not similarities:
            return []
            
        sim_scores_dict = {sim.similar_movie_id: sim.similarity_score for sim in similarities}
        similar_movie_ids = list(sim_scores_dict.keys())

        # Fetch actual movie details
        query = (
            self.session.query(Movie)
            .filter(Movie.id.in_(similar_movie_ids))
        )
        
        if genre_filter:
            query = query.filter(Movie.genres.any(Genre.name.in_(genre_filter)))
            
        if max_runtime:
            query = query.filter(Movie.runtime <= max_runtime)
        if min_score:
            query = query.filter(Movie.audience_score >= min_score)
        if language:
            query = query.filter(Movie.language == language)

        movies = query.all()
        
        # Sort by the precomputed similarity score
        movies = sorted(movies, key=lambda m: sim_scores_dict.get(m.id, 0), reverse=True)

        return [
            {
                "id": m.id,
                "title": m.title,
                "release_year": m.release_year,
                "poster_url": m.poster_url,
                "overview": m.overview,
                "runtime": m.runtime,
                "language": m.language,
                "audience_score": m.audience_score,
                "score": float(sim_scores_dict.get(m.id, 0)),
                "genres": [g.name for g in m.genres]
            }
            for m in movies[:top_n]
        ]
