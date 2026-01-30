from sqlalchemy.orm import Session
from sqlalchemy import func, case, DATE
from app.models.feedback_models import UserFeedback

def get_strategy_evolution_metrics(session: Session, days: int = 30):
    """
    Returns daily performance trends (CTR) per strategy.
    Groups by day and strategy.
    """
    # SQLite DATE function alias: func.date(UserFeedback.timestamp)
    day_expr = func.date(UserFeedback.timestamp).label("day")
    likes_expr = func.sum(case((UserFeedback.liked == 1, 1), else_=0))
    total_expr = func.count(UserFeedback.id)
    ctr_expr = 1.0 * likes_expr / total_expr

    return (
        session.query(
            day_expr,
            UserFeedback.strategy,
            total_expr.label("impressions"),
            likes_expr.label("likes"),
            ctr_expr.label("ctr")
        )
        .group_by(day_expr, UserFeedback.strategy)
        .order_by(day_expr.desc())
        .limit(days * 10) # rough estimate to cover multiple strategies per day
        .all()
    )
