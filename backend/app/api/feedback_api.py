from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.feedback_models import UserFeedback
from app.models.recommendation_log import RecommendationLog
from app.ml.strategy_lookup import get_last_strategy_for_user
from app.ml.strategy_learning import update_strategy_weight
from app.ml.engagement_tracker import update_engagement
from app.ml.engagement_tracker import update_engagement

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("/")
def submit_feedback(
    user_id: int, 
    movie_id: int, 
    liked: int = None, 
    rating: float = None, 
    strategy_name: str = None, 
    db: Session = Depends(get_db)
):
    """
    Submit user feedback (like/dislike or rating) for a movie.
    The system automatically identifies the underlying strategy from logs
    to update personalization weights via Reinforcement Learning (Phase 13).
    """
    # 1. Identify Strategy (if not provided)
    active_strategy = strategy_name
    if not active_strategy:
        active_strategy = get_last_strategy_for_user(user_id)

    # 2. Record Feedback
    feedback = UserFeedback(
        user_id=str(user_id), 
        movie_id=movie_id, 
        liked=liked, 
        rating=rating,
        strategy=active_strategy  # Direct attribution if available
    )
    db.add(feedback)
    db.commit()

    # 3. Apply Online Learning Loop (Phase 17.2)
    # If strategy wasn't in feedback, look it up from logs as the source of truth
    identifiable_strategy = feedback.strategy
    if not identifiable_strategy:
        last_log = (
            db.query(RecommendationLog)
            .filter_by(user_id=user_id)
            .order_by(RecommendationLog.id.desc())
            .first()
        )
        if last_log:
            identifiable_strategy = last_log.strategy
            # Optional: Backfill the strategy in the feedback record
            feedback.strategy = identifiable_strategy
            db.commit()

    if identifiable_strategy:
        update_strategy_weight(
            session=db,
            user_id=user_id,
            strategy=identifiable_strategy,
            liked=bool(liked)
        )

    # 4. Update Engagement Health (Phase 18.3)
    update_engagement(
        session=db,
        user_id=user_id,
        liked=bool(liked)
    )

    # 4. Update Engagement Health (Step 4)
    update_engagement(
        session=db,
        user_id=user_id,
        liked=bool(liked)
    )

    db.refresh(feedback)
    return {
        "status": "success", 
        "feedback_id": feedback.id,
        "strategy_rewarded": active_strategy
    }
