from sqlalchemy.orm import Session

from app.ml.recommender import Recommender
from app.ml.content_recommender import ContentRecommender
from app.ml.popularity_recommender import PopularityRecommender
from app.ml.score_adjuster import apply_intent_boosts
from app.models.base_models import Rating, Movie
from app.models.recommendation_log import RecommendationLog
from app.models.strategy_stats import StrategyStats
from app.models.user_strategy_stats import UserStrategyStats

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

    def _get_best_strategy(self, user_id: int, available_strategies: list[str]) -> str:
        """
        Priority:
        1. User-specific weights if available (Phase 12)
        2. Global performance weights as fallback (Phase 11.1)
        """
        # 1. Check User-Specific Stats
        user_stats = (
            self.session.query(UserStrategyStats)
            .filter(UserStrategyStats.user_id == user_id)
            .filter(UserStrategyStats.strategy.in_(available_strategies))
            .order_by(UserStrategyStats.weight.desc())
            .first()
        )
        # We only use user stats if there is actually some local history (total_used > 0)
        if user_stats and user_stats.total_used > 0:
            return user_stats.strategy

        # 2. Fallback to Global
        global_stats = (
            self.session.query(StrategyStats)
            .filter(StrategyStats.strategy_name.in_(available_strategies))
            .order_by(StrategyStats.weight.desc())
            .first()
        )
        return global_stats.strategy_name if global_stats else available_strategies[0]

    def recommend(
        self, 
        user_id: int, 
        top_n: int = 10, 
        genres: list[str] | None = None,
        mood: str | None = None,
        time_context: str | None = None,
        preferred_strategy: str | None = None
    ):
        rating_count = self._user_rating_count(user_id)
        candidate_count = top_n * 5

        # 1. Identify Viable Strategies
        viable = ["popularity-based"]
        if rating_count >= self.min_ratings:
            viable.append("collaborative-filtering")
            viable.append("content-based") # User has enough for both
        elif rating_count > 0:
            viable.append("content-based")

        # 2. Select Best Strategy based on Weight
        if preferred_strategy and preferred_strategy in viable:
            strategy = preferred_strategy
        else:
            strategy = self._get_best_strategy(user_id, viable)
        results = []
        reason = ""

        # 3. Execute Selected Strategy
        if strategy == "collaborative-filtering":
            results = self.cf.recommend(str(user_id), candidate_count, genre_filter=genres)
            reason = "User has sufficient interaction history; using collaborative taste."
            for movie in results:
                movie["explanation"] = self._cf_explanation()

        elif strategy == "content-based":
            results = self._content_fallback(user_id, candidate_count, genre_filter=genres)
            reason = "User has some history; matched against your liked movie genres."

        # FALLBACK (Safety)
        if not results:
            results = self.popular.recommend(candidate_count, genre_filter=genres)
            strategy = "popularity-based"
            reason = "Using globally trending movies for best experience."
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

        # Strategy logging is now handled by record_strategy_use in recommender_interface.py
        
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
