from app.models.user_strategy_stats import UserStrategyStats

def get_or_create_user_strategy(db, user_id: int, strategy: str):
    """
    Lazily initializes a strategy stats row for a specific user.
    """
    row = (
        db.query(UserStrategyStats)
        .filter_by(user_id=user_id, strategy=strategy)
        .first()
    )

    if not row:
        row = UserStrategyStats(
            user_id=user_id,
            strategy=strategy
        )
        db.add(row)
        db.commit()
        db.refresh(row)

    return row
