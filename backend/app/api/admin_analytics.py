from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.analytics.strategy_metrics import get_strategy_metrics
from app.analytics.analytics_service import AnalyticsService

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

@router.get("/churn")
def get_churn_risk_analysis(db: Session = Depends(get_db)):
    """
    Identifies users at risk of churning based on disengagement signals.
    """
    service = AnalyticsService(db)
    return service.get_churn_analysis()

@router.get("/evolution")
def get_strategy_evolution(days: int = 30, db: Session = Depends(get_db)):
    """
    Detailed time-series of strategy performance.
    """
    service = AnalyticsService(db)
    return service.get_strategy_evolution(days=days)
