from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.feedback_models import UserFeedback

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("/")
def submit_feedback(user_id: int, movie_id: int, liked: int = None, rating: float = None, db: Session = Depends(get_db)):
    """
    Submit user feedback (like/dislike or rating) for a movie.
    This data is immediately recorded and used for future recommendations.
    """
    # Convert user_id to string to match our database ID cleanup conventions
    feedback = UserFeedback(
        user_id=str(user_id), 
        movie_id=movie_id, 
        liked=liked, 
        rating=rating
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"status": "success", "feedback_id": feedback.id}
