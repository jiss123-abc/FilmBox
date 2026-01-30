from sqlalchemy.orm import Session
from app.models.user_engagement_stats import UserEngagementStats

def get_engagement_score(
    session: Session,
    user_id: any
) -> float:
    """
    Fetches the persistent engagement score for a user.
    Returns 0.0 (Neutral/At-Risk boundary) if no stats exist.
    """
    user_id_str = str(user_id)
    stats = (
        session.query(UserEngagementStats)
        .filter_by(user_id=user_id_str)
        .first()
    )

    if not stats:
        return 0.0

    return stats.engagement_score
