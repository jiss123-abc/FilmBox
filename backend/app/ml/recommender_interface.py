from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.ml.hybrid_recommender import HybridRecommender
from app.ml.strategy_selector import select_best_strategy
from app.ml.strategy_tracker import record_strategy_use
from app.ml.recommendation_logger import log_recommendation_event
from app.experiments.assignment import get_or_assign_strategy, EXPERIMENT_GROUP

def get_strategy_for_user(user_id: int, use_experiment: bool = False) -> str:
    """
    Selects strategy:
    - Adaptive (Phase 16): Based on weights + exploration.
    - Experimental (Phase 14): Fixed assignment if flag is true.
    """
    if use_experiment:
        return get_or_assign_strategy(user_id)
    
    return select_best_strategy(user_id)


def get_hybrid_recommendations(user_id: int, top_n: int = 10, genres=None):
    """
    Orchestrates the recommendation flow:
    1. Select strategy (Experimental Override)
    2. Fetch recommendations from the hybrid recommender
    3. Record strategy usage for learning
    4. Log recommendation event for analytics
    """
    session: Session = SessionLocal()
    try:
        # Phase 14: Use experiment-assigned strategy
        strategy = get_strategy_for_user(user_id)

        hybrid = HybridRecommender(session)
        result = hybrid.recommend(
            user_id=user_id,
            top_n=top_n,
            genres=genres,
            preferred_strategy=strategy
        )

        # The hybrid.recommend return dict contains a list of movies under 'recommendations'
        # We need to extract them to match the original return format and for tracking.
        recommendations = result.get("recommendations", [])

        # Standardize for consumption
        formatted_recs = []
        for movie in recommendations:
            formatted_recs.append({
                "movie_id": movie.get("id") or movie.get("movie_id"),
                "title": movie.get("title"),
                "explanation": movie.get("explanation", ""),
                "strategy": strategy
            })

        record_strategy_use(user_id, strategy)

        log_recommendation_event(
            user_id=user_id,
            strategy=strategy,
            num_recommendations=len(formatted_recs),
            experiment_group=None # Phase 16: Not in experiment by default
        )

        return formatted_recs[:top_n]

    finally:
        session.close()
