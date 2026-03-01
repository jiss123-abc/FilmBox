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


from app.ml.engagement_reader import get_engagement_score
from app.ml.adaptive_strategy import select_adaptive_strategy
from app.ml.exploration_logic import apply_exploration
from app.ml.decay import decay_preferences
from app.ml.preference_reader import get_genre_preferences
from app.ml.taste_bias import apply_taste_bias
from app.ml.safety_controls import SafetyEnforcer

def get_hybrid_recommendations(
    user_id: int, 
    top_n: int = 10, 
    genres=None,
    mood=None,
    time_context=None,
    max_runtime=None,
    min_score=None,
    max_score=None,
    language=None,
    min_year=None
):
    """
    Orchestrates the recommendation flow:
    1. Select strategy (Adaptive via Phase 19)
    2. Decay old preferences (Phase 20)
    3. Fetch recommendations from the hybrid recommender
    4. Apply Taste Bias (Phase 20)
    5. Apply Exploration (Diversity Injection)
    6. Record strategy usage & Log event
    """
    session: Session = SessionLocal()
    try:
        # Phase 19: Adaptive Strategy Switching
        base_strategy = select_best_strategy(user_id)
        
        engagement = get_engagement_score(session, user_id)
        
        adaptive_result = select_adaptive_strategy(base_strategy, engagement)
        
        final_strategy = adaptive_result["strategy"]
        exploration_rate = adaptive_result.get("exploration", 0.0)
 
        # Phase 20: Decay Preferences ("Memory Fading")
        decay_preferences(session, user_id)
        
        # Phase 20: Fetch Active Preferences
        genre_weights = get_genre_preferences(session, user_id)
 
        hybrid = HybridRecommender(session)
        result = hybrid.recommend(
            user_id=user_id,
            top_n=top_n, # Fetch same amount, we re-rank/shuffle in place
            genres=genres,
            mood=mood,
            time_context=time_context,
            max_runtime=max_runtime,
            min_score=min_score,
            max_score=max_score,
            language=language,
            min_year=min_year,
            preferred_strategy=final_strategy
        )

        # The hybrid.recommend return dict contains a list of movies under 'recommendations'
        # We need to extract them to match the original return format and for tracking.
        recommendations = result.get("recommendations", [])
        
        # Phase 20: Apply Taste Bias (Re-ranking)
        recommendations = apply_taste_bias(recommendations, genre_weights)
        
        # Phase 19.2: Apply Exploration (Diversity Shuffling)
        recommendations = apply_exploration(recommendations, exploration_rate)

        # Phase 21.2: Safety Controls (Production Gate)
        recommendations = SafetyEnforcer.filter_low_confidence(recommendations)
        recommendations = SafetyEnforcer.enforce_limits(recommendations, top_n)

        # Standardize for consumption
        formatted_recs = []
        for movie in recommendations:
            formatted_recs.append({
                "movie_id": movie.get("id") or movie.get("movie_id"),
                "title": movie.get("title"),
                "explanation": movie.get("explanation", ""),
                "strategy": final_strategy,
                "runtime": movie.get("runtime"),
                "language": movie.get("language"),
                "poster_url": movie.get("poster_url"),
                "audience_score": movie.get("audience_score"),
                "overview": movie.get("overview"),
                "genres": movie.get("genres", [])
            })

        record_strategy_use(user_id, final_strategy)

        # Extract IDs
        rec_ids = [r["movie_id"] for r in formatted_recs]

        log_recommendation_event(
            user_id=user_id,
            strategy=final_strategy,
            num_recommendations=len(formatted_recs),
            experiment_group=None, # Phase 16: Not in experiment by default
            movie_ids=rec_ids
        )

        return formatted_recs[:top_n]

    finally:
        session.close()
