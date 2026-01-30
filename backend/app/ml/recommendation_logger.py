from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.recommendation_log import RecommendationLog


def log_recommendation_event(
    user_id: int,
    strategy: str,
    num_recommendations: int,
    experiment_group: str = None
):
    session: Session = SessionLocal()

    log = RecommendationLog(
        user_id=user_id,
        strategy=strategy,
        num_recommendations=num_recommendations,
        experiment_group=experiment_group
    )

    session.add(log)
    session.commit()
    session.close()
