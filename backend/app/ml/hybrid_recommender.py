from sqlalchemy.orm import Session

from app.ml.recommender import Recommender
from app.ml.content_recommender import ContentRecommender
from app.ml.popularity_recommender import PopularityRecommender
from app.ml.score_adjuster import apply_intent_boosts
from app.models.base_models import Rating, Movie

class HybridRecommender:
    def __init__(self, session: Session, min_ratings: int = 5):
        self.session = session
        self.min_ratings = min_ratings
        self.cf = Recommender(session)
        self.cb = ContentRecommender(session)
        self.popular = PopularityRecommender(session)

    def _user_rating_count(self, user_id: int) -> int:
        return (
            self.session.query(Rating)
            .filter(Rating.user_id == str(user_id))
            .count()
        )

    def recommend(
        self, 
        user_id: int, 
        top_n: int = 10, 
        genres: list[str] | None = None,
        mood: str | None = None,
        time_context: str | None = None
    ):
        rating_count = self._user_rating_count(user_id)
        
        # Buffer candidates for re-ranking
        candidate_count = top_n * 5

        # --- CANDIDATE SELECTION ---
        results = []
        strategy = "none"
        reason = ""

        # CASE 1 — Active user
        if rating_count >= self.min_ratings:
            results = self.cf.recommend(str(user_id), candidate_count, genre_filter=genres)
            strategy = "collaborative-filtering"
            reason = "User has sufficient interaction history"
            for movie in results:
                movie["explanation"] = self._cf_explanation()

        # CASE 2 — Cold start with some ratings
        elif rating_count > 0:
            results = self._content_fallback(user_id, candidate_count, genre_filter=genres)
            if results:
                strategy = "content-based"
                reason = "User has limited history; using content similarity"

        # CASE 3 — Absolute cold start (no ratings)
        if not results:
            results = self.popular.recommend(candidate_count, genre_filter=genres)
            strategy = "popularity-based"
            reason = "New user or strict filter; using trending items"
            for movie in results:
                movie["explanation"] = self._popularity_explanation(
                    movie.get("rating_count", 0),
                    movie.get("avg_rating", 0)
                )

        # --- INTENT-AWARE RE-RANKING (Phase 8) ---
        if results:
            results = apply_intent_boosts(
                recommendations=results,
                intent=strategy,
                genres=genres,
                mood=mood,
                time_context=time_context
            )
            
            # --- PRESERVE EXPLAINABILITY (Step 4) ---
            if mood or time_context:
                for movie in results:
                    movie["explanation"] += " Adjusted for your mood and timing preferences."

        return {
            "strategy": strategy,
            "reason": reason,
            "recommendations": results[:top_n]
        }

    def _content_fallback(self, user_id: int, top_n: int, genre_filter: list[str] | None = None):
        """
        Use the user's highest-rated movie(s) to seed content-based recommendations.
        """
        top_rated = (
            self.session.query(Rating)
            .filter(Rating.user_id == str(user_id))
            .order_by(Rating.rating.desc())
            .first()
        )

        if not top_rated:
            return []

        seed_movie = self.session.query(Movie).get(top_rated.movie_id)

        results = self.cb.recommend_similar_movies(
            movie_id=top_rated.movie_id,
            top_n=top_n
        )

        for movie in results:
            movie["explanation"] = self._content_explanation(seed_movie.title)

        return results

    def _cf_explanation(self):
        return "Recommended because users with similar tastes liked this movie."

    def _content_explanation(self, seed_movie_title: str):
        return f"Recommended because it shares similar genres with '{seed_movie_title}'."

    def _popularity_explanation(self, rating_count: int, avg_rating: float):
        return (
            f"Popular among {rating_count}+ users "
            f"with an average rating of {avg_rating}."
        )
