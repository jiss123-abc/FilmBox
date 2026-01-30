from sqlalchemy.orm import Session
from app.models.recommendation_log import RecommendationLog
from app.models.strategy_stats import StrategyStats
from app.ml.strategy_weighting import recalculate_weights
from app.ml.user_strategy_utils import get_or_create_user_strategy
from app.ml.user_strategy_weighting import recalculate_user_strategy_weight

from app.ml.strategy_lookup import get_last_strategy_for_user

def find_last_strategy_used(db: Session, user_id: int) -> str:
    """
    Wrapper for standardized lookup utility.
    """
    return get_last_strategy_for_user(user_id)

def apply_feedback_to_strategy(db: Session, user_id: int, strategy: str, liked: int):
    """
    Updates the weight for a strategy based on feedback.
    👍 liked=1 -> Reward (positive_feedback += 1)
    👎 liked=0 -> Penalty (total_used += 1, dilution occurs)
    """
    if not strategy:
        return

    # 1. Update Global Stats (Phase 11.1)
    global_stat = db.query(StrategyStats).filter_by(strategy_name=strategy).first()
    if global_stat:
        if liked == 1:
            global_stat.likes_received += 1
        # In reinforcement learning, a 'use' without a 'like' is a natural penalty
        # because the success rate decreases.
        recalculate_weights(db)
        db.commit()

    # 2. Update User-Specific Stats (Phase 13)
    user_row = get_or_create_user_strategy(db, user_id, strategy)
    if liked == 1:
        user_row.positive_feedback += 1
    
    # Note: record_strategy_use already increments total_used during the recommendation.
    # Here we only increment positive_feedback if it was a success.
    # If it was a dislike (liked=0), the weight will stay diluted.
    
    recalculate_user_strategy_weight(user_row)
    db.commit()
