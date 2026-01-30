from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user_strategy_stats import UserStrategyStats

LIKE_BOOST = 1.0
DISLIKE_PENALTY = 0.3
MIN_WEIGHT = 0.1


def update_strategy_weight(
    session: Session,
    user_id: int,
    strategy: str,
    liked: bool
):
    """
    Core reinforcement learning logic:
    - Increases weight for successful recommendations.
    - Decreases weight for failures (Likes/Dislikes).
    - Ensures strategies are promoted/demoted deterministically.
    """
    stat = (
        session.query(UserStrategyStats)
        .filter_by(user_id=user_id, strategy=strategy)
        .first()
    )

    if not stat:
        stat = UserStrategyStats(
            user_id=user_id,
            strategy=strategy,
            weight=1.0
        )
        session.add(stat)

    if liked:
        stat.weight += LIKE_BOOST
    else:
        stat.weight = max(MIN_WEIGHT, stat.weight - DISLIKE_PENALTY)

    stat.updated_at = datetime.utcnow()
    session.commit()
