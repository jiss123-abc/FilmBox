from app.models.user_genre_preferences import UserGenrePreferences
from sqlalchemy.orm import Session

DECAY_RATE = 0.98  # Per interaction cycle

def decay_preferences(session: Session, user_id: any):
    """
    Applies a decay factor to all genre preferences for a user.
    Ensures old tastes fade over time.
    """
    user_id_str = str(user_id)
    prefs = (
        session.query(UserGenrePreferences)
        .filter_by(user_id=user_id_str)
        .all()
    )

    for pref in prefs:
        pref.weight *= DECAY_RATE

    session.commit()
