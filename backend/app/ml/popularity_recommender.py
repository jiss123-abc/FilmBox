from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.base_models import Movie, Rating, Genre


class PopularityRecommender:
    def __init__(self, session: Session, min_votes: int = 50):
        self.session = session
        self.min_votes = min_votes

    def recommend(self, top_n: int = 10, genre_filter: list[str] | None = None):
        """
        Recommend globally popular movies based on
        average rating and number of ratings.
        Optional genre_filter scopes results.
        """
        query = (
            self.session.query(
                Movie.id,
                Movie.title,
                Movie.release_year,
                func.avg(Rating.rating).label("avg_rating"),
                func.count(Rating.user_id).label("rating_count")
            )
            .join(Rating, Rating.movie_id == Movie.id)
        )

        if genre_filter:
            # Note: The above is a bit complex in SQLAlchemy for many-to-many.
            # A simpler way if genres is a relationship:
            query = query.filter(Movie.genres.any(Genre.name.in_(genre_filter)))

        movies = (
            query
            .group_by(Movie.id)
            .having(func.count(Rating.user_id) >= self.min_votes)
            .order_by(
                func.avg(Rating.rating).desc(),
                func.count(Rating.user_id).desc()
            )
            .limit(top_n)
            .all()
        )

        return [
            {
                "id": m.id,
                "title": m.title,
                "release_year": m.release_year,
                "avg_rating": round(float(m.avg_rating), 2),
                "rating_count": m.rating_count,
                "score": round(float(m.avg_rating), 2), # Use average rating as base score
                "num_ratings": m.rating_count,          # Used by score adjuster
                "genres": [g.name for g in self.session.query(Movie).get(m.id).genres] # Need genres for boosts
            }
            for m in movies
        ]
