from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user_strategy_stats import UserStrategyStats

DEFAULT_ORDER = [
    "collaborative-filtering",
    "content-based",
    "popularity-based"
]

def select_best_strategy(user_id: int) -> str:
    session: Session = SessionLocal()

    stats = (
        session.query(UserStrategyStats)
        .filter(UserStrategyStats.user_id == user_id)
        .all()
    )

    # Convert to sets for easy comparison
    used_strategies = {s.strategy for s in stats}
    
    # 1. Exploration: Try strategies that haven't been used yet
    for strategy in DEFAULT_ORDER:
        if strategy not in used_strategies:
            session.close()
            return strategy

    # 2. Exploitation: Pick the best-performing one
    best_stat = (
        session.query(UserStrategyStats)
        .filter(UserStrategyStats.user_id == user_id)
        .order_by(UserStrategyStats.weight.desc())
        .first()
    )
    
    session.close()
    return best_stat.strategy if best_stat else DEFAULT_ORDER[0]
