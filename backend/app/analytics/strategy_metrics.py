from sqlalchemy.orm import Session
from sqlalchemy import func, case, Float
from app.models.feedback_models import UserFeedback

def get_strategy_metrics(session: Session):
    """
    Returns the global leaderboard of strategies based on user feedback.
    """
    likes_expr = func.sum(case((UserFeedback.liked == 1, 1), else_=0))
    impressions_expr = func.count(UserFeedback.id)
    ctr_expr = 1.0 * likes_expr / impressions_expr

    return (
        session.query(
            UserFeedback.strategy,
            impressions_expr.label("impressions"),
            likes_expr.label("likes"),
            ctr_expr.label("ctr")
        )
        .group_by(UserFeedback.strategy)
        .order_by(ctr_expr.desc())
        .all()
    )
