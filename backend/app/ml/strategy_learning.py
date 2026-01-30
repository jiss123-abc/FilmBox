from sqlalchemy.orm import Session
from app.models.user_strategy_stats import UserStrategyStats

REWARD = 1.0
PENALTY = -1.0

def update_strategy_weight(
    session: Session,
    user_id: int,
    strategy: str,
    liked: bool
):
    """
    Updates the weight of a strategy based on user feedback.
    👍 LIKE -> +1.0
    👎 DISLIKE -> -1.0
    """
    delta = REWARD if liked else PENALTY

    record = (
        session.query(UserStrategyStats)
        .filter_by(user_id=user_id, strategy=strategy)
        .first()
    )

    if record:
        record.weight += delta
    else:
        record = UserStrategyStats(
            user_id=user_id,
            strategy=strategy,
            weight=delta
        )
        session.add(record)

    session.commit()
