from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.feedback_models import UserFeedback

def get_user_engagement_metrics(session: Session):
    """
    Returns engagement scores for all users based on their feedback history.
    Score = 1.0 * Likes / Total Interactions
    """
    likes_expr = func.sum(case((UserFeedback.liked == 1, 1), else_=0))
    total_expr = func.count(UserFeedback.id)
    score_expr = 1.0 * likes_expr / total_expr

    return (
        session.query(
            UserFeedback.user_id,
            total_expr.label("total_interactions"),
            likes_expr.label("likes"),
            score_expr.label("engagement_score")
        )
        .group_by(UserFeedback.user_id)
        .order_by(score_expr.desc())
        .all()
    )
