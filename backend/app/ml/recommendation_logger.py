from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.recommendation_log import RecommendationLog


def log_recommendation_event(
    user_id: int,
    strategy: str,
    num_recommendations: int,
    experiment_group: str = None,
    movie_ids: list = None # New for Phase 21: List of ints
):
    session: Session = SessionLocal()

    # Convert list to CSV string
    movie_ids_str = ",".join(map(str, movie_ids)) if movie_ids else ""

    log = RecommendationLog(
        user_id=user_id,
        strategy=strategy,
        num_recommendations=num_recommendations,
        experiment_group=experiment_group,
        movie_ids=movie_ids_str
    )

    session.add(log)
    session.commit()
    session.close()
