from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user_strategy_stats import UserStrategyStats


def record_strategy_use(user_id: int, strategy: str):
    session: Session = SessionLocal()

    stat = (
        session.query(UserStrategyStats)
        .filter_by(user_id=user_id, strategy=strategy)
        .first()
    )

    if not stat:
        stat = UserStrategyStats(
            user_id=user_id,
            strategy=strategy,
            total_used=1,
            positive_feedback=0,
            weight=1.0
        )
        session.add(stat)
    else:
        stat.total_used += 1

    session.commit()
    session.close()
