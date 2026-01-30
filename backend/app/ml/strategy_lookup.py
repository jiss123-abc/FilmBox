from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.recommendation_log import RecommendationLog


def get_last_strategy_for_user(user_id: int) -> str | None:
    session: Session = SessionLocal()

    log = (
        session.query(RecommendationLog)
        .filter(RecommendationLog.user_id == user_id)
        .order_by(RecommendationLog.created_at.desc())
        .first()
    )

    session.close()

    return log.strategy if log else None
