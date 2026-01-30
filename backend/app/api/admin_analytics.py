from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.analytics.strategy_metrics import get_strategy_metrics

router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])


@router.get("/strategies")
def strategy_performance(db: Session = Depends(get_db)):
    """
    Returns the global performance leaderboard of all recommendation strategies.
    """
    results = get_strategy_metrics(db)
    return [
        {
            "strategy": r.strategy,
            "impressions": r.impressions,
            "likes": r.likes,
            "ctr": round(float(r.ctr), 3) if r.ctr is not None else 0
        }
        for r in results
    ]
