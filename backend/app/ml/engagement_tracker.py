from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user_engagement_stats import UserEngagementStats

def update_engagement(
    session: Session,
    user_id: any,
    liked: bool
):
    """
    Updates user engagement health after a feedback event.
    Formula: (Positive - Negative) / max(Total, 1)
    """
    user_id_str = str(user_id)
    stats = (
        session.query(UserEngagementStats)
        .filter_by(user_id=user_id_str)
        .first()
    )

    if not stats:
        stats = UserEngagementStats(
            user_id=user_id_str,
            total_recommendations=0,
            positive_feedback=0,
            negative_feedback=0
        )
        session.add(stats)

    stats.total_recommendations += 1

    if liked:
        stats.positive_feedback += 1
    else:
        stats.negative_feedback += 1

    stats.last_interaction = datetime.utcnow()

    # Calculate Engagement Score (Step 2)
    stats.engagement_score = (
        (stats.positive_feedback - stats.negative_feedback)
        / max(stats.total_recommendations, 1)
    )

    session.commit()
