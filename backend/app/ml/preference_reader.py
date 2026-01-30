from sqlalchemy.orm import Session
from app.models.user_genre_preferences import UserGenrePreferences

def get_genre_preferences(session: Session, user_id: any) -> dict[str, float]:
    """
    Retrieves the current genre preference map for a user.
    Returns: { "Action": 0.5, "Drama": -0.2 }
    """
    user_id_str = str(user_id)
    prefs = (
        session.query(UserGenrePreferences)
        .filter_by(user_id=user_id_str)
        .all()
    )
    return {p.genre: p.weight for p in prefs}
