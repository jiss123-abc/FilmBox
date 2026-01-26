from app.core.database import SessionLocal
from app.models.feedback_models import UserFeedback

def check_feedback():
    session = SessionLocal()
    try:
        feedbacks = session.query(UserFeedback).all()
        if not feedbacks:
            print("No feedback found in the database.")
            return
            
        print(f"{'ID':<5} | {'User ID':<10} | {'Movie ID':<10} | {'Liked':<5} | {'Rating':<6}")
        print("-" * 50)
        for fb in feedbacks:
            print(f"{fb.id:<5} | {fb.user_id:<10} | {fb.movie_id:<10} | {fb.liked:<5} | {fb.rating:<6}")
    finally:
        session.close()

if __name__ == "__main__":
    check_feedback()
