from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.strategy_stats import StrategyStats
from app.models.feedback_models import UserFeedback
from app.models.recommendation_log import RecommendationLog
from app.analytics.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/admin", tags=["Admin Analytics"])

@router.get("/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    """
    Returns high-level system performance metrics and strategy weights.
    """
    
    # 1. Strategy Performance
    stats = db.query(StrategyStats).all()
    strategy_metrics = [
        {
            "name": s.strategy_name,
            "times_used": s.times_used,
            "likes_received": s.likes_received,
            "weight": round(s.weight, 4),
            "conversion_rate": round(s.likes_received / s.times_used, 4) if s.times_used > 0 else 0
        }
        for s in stats
    ]
    
    # 2. General Feedback Stats
    total_likes = db.query(UserFeedback).filter(UserFeedback.liked == 1).count()
    total_dislikes = db.query(UserFeedback).filter(UserFeedback.liked == 0).count()
    
    # 3. Recent Activity (Last 24 Hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_recs = db.query(RecommendationLog).filter(RecommendationLog.created_at >= last_24h).count()
    recent_feedback = db.query(UserFeedback).filter(UserFeedback.timestamp >= last_24h).count()
    
    # 4. Strategy Effectiveness (Phase 12.2)
    # Join RecommendationLogs with UserFeedback to see which strategy converts best
    effectiveness_query = db.query(
        RecommendationLog.strategy,
        func.count(UserFeedback.id).label("total_feedback"),
        func.sum(func.case((UserFeedback.liked == 1, 1), else_=0)).label("positive_feedback")
    ).join(
        UserFeedback, RecommendationLog.user_id == UserFeedback.user_id
    ).group_by(RecommendationLog.strategy).all()

    effectiveness_metrics = [
        {
            "strategy": row.strategy,
            "total_feedback": row.total_feedback,
            "positive_feedback": int(row.positive_feedback or 0),
            "success_rate": round(float(row.positive_feedback or 0) / row.total_feedback, 2) if row.total_feedback > 0 else 0
        }
        for row in effectiveness_query
    ]
    
    # 5. User Engagement (Phase 12.3)
    # Track how many recs and likes each user has
    engagement_query = db.query(
        RecommendationLog.user_id,
        func.count(RecommendationLog.id).label("total_recommendations")
    ).group_by(RecommendationLog.user_id).all()

    engagement_metrics = []
    for row in engagement_query:
        # Get likes for this specific user
        likes_count = db.query(UserFeedback).filter(
            UserFeedback.user_id == str(row.user_id),
            UserFeedback.liked == 1
        ).count()
        
        engagement_metrics.append({
            "user_id": row.user_id,
            "total_recommendations": row.total_recommendations,
            "total_likes": likes_count,
            "personalization_score": round(likes_count / row.total_recommendations, 2) if row.total_recommendations > 0 else 0
        })
    
    # 7. A/B Experiment Results (Phase 14.5)
    experiment_group = "phase14_ab"
    ab_results_query = db.query(
        RecommendationLog.strategy,
        func.count(UserFeedback.id).label("impressions"),
        func.sum(func.case((UserFeedback.liked == 1, 1), else_=0)).label("likes")
    ).join(
        UserFeedback, RecommendationLog.user_id == UserFeedback.user_id
    ).filter(
        RecommendationLog.experiment_group == experiment_group
    ).group_by(RecommendationLog.strategy).all()

    ab_metrics = [
        {
            "strategy": row.strategy,
            "impressions": row.impressions,
            "likes": int(row.likes or 0),
            "ctr": round(float(row.likes or 0) / row.impressions, 3) if row.impressions > 0 else 0
        }
        for row in ab_results_query
    ]

    # Placeholder for distribution_metrics, as it's referenced in the return but not defined in the provided code.
    # Assuming it would be defined similarly to other metrics.
    distribution_metrics = {} # Or fetch from AnalyticsService if intended

    return {
        "status": "active",
        "timestamp": datetime.utcnow(),
        "strategies": strategy_metrics,
        "effectiveness": effectiveness_metrics,
        "engagement": engagement_metrics,
        "distribution": distribution_metrics,
        "ab_test": {
            "experiment": experiment_group,
            "results": ab_metrics
        },
        "global_stats": {
            "total_likes": total_likes,
            "total_dislikes": total_dislikes,
            "feedback_ratio": round(total_likes / (total_likes + total_dislikes), 2) if (total_likes + total_dislikes) > 0 else 0
        },
        "activity_24h": {
            "recommendations_served": recent_recs,
            "feedback_received": recent_feedback
        }
    }

@router.get("/analytics/trends")
def get_strategy_trends(days: int = 7, db: Session = Depends(get_db)):
    """
    Returns daily performance trends (CTR) for each strategy.
    """
    service = AnalyticsService(db)
    return service.get_strategy_performance_timeline(days=days)

@router.get("/analytics/pulse")
def get_system_pulse(db: Session = Depends(get_db)):
    """
    Returns a real-time snapshot of system activity (velocity, engagement).
    """
    service = AnalyticsService(db)
    return {
        "pulse": service.get_pulse_metrics(),
        "dominance": service.get_strategy_dominance()
    }

@router.get("/analytics/user-engagement")
def get_user_engagement(db: Session = Depends(get_db)):
    """
    Returns engagement scores for all users.
    """
    service = AnalyticsService(db)
    return service.get_user_engagement()

@router.get("/analytics/evolution")
def get_strategy_evolution(days: int = 30, db: Session = Depends(get_db)):
    """
    Returns daily performance trends for all strategies.
    This maps the "learning curve" of the recommender.
    """
    service = AnalyticsService(db)
    return service.get_strategy_evolution(days=days)
