from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user_genre_preferences import UserGenrePreferences

LIKE_BOOST = 0.2
DISLIKE_PENALTY = 0.3

def update_genre_preferences(
    session: Session,
    user_id: any,
    genres: list[str],
    liked: bool
):
    """
    Updates long-term genre preferences for a user.
    Like -> Boost weight.
    Dislike -> Penalize weight.
    """
    user_id_str = str(user_id)
    delta = LIKE_BOOST if liked else -DISLIKE_PENALTY

    for genre in genres:
        # Normalize genre string if needed (lowercase etc)
        normalized_genre = genre.strip()
        
        pref = (
            session.query(UserGenrePreferences)
            .filter_by(user_id=user_id_str, genre=normalized_genre)
            .first()
        )

        if not pref:
            pref = UserGenrePreferences(
                user_id=user_id_str,
                genre=normalized_genre,
                weight=delta
            )
            session.add(pref)
        else:
            pref.weight += delta
            # Ensure last_updated is refreshed (it's auto-handled by onupdate in model but good to be explicit/safe)
            pref.last_updated = datetime.utcnow()

    session.commit()
