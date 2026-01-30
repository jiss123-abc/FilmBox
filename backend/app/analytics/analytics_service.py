from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.recommendation_log import RecommendationLog
from app.models.feedback_models import UserFeedback
from app.models.strategy_stats import StrategyStats
from app.analytics.user_engagement import get_user_engagement_metrics
from app.analytics.strategy_trends import get_strategy_evolution_metrics

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_strategy_evolution(self, days: int = 30):
        """
        Returns daily CTR trends per strategy.
        """
        return get_strategy_evolution_metrics(self.db, days=days)

    def get_strategy_performance_timeline(self, days: int = 7):
        """
        Returns daily CTR (Click-Through Rate) per strategy.
        Used for legacy support or combined views.
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        timeline_query = self.db.query(
            func.strftime('%Y-%m-%d', RecommendationLog.created_at).label('date'),
            RecommendationLog.strategy,
            func.count(RecommendationLog.id).label('impressions')
        ).filter(
            RecommendationLog.created_at >= start_date
        ).group_by(
            'date', RecommendationLog.strategy
        ).all()
        
        results = []
        for row in timeline_query:
            likes_count = self.db.query(UserFeedback).filter(
                UserFeedback.strategy == row.strategy,
                func.strftime('%Y-%m-%d', UserFeedback.timestamp) == row.date,
                UserFeedback.liked == 1
            ).count()

            results.append({
                "date": row.date,
                "strategy": row.strategy,
                "impressions": row.impressions,
                "likes": likes_count,
                "ctr": round(likes_count / row.impressions, 3) if row.impressions > 0 else 0
            })
            
        return results

    def get_pulse_metrics(self):
        """
        High-frequency 'Heartbeat' of the system (Last 60 minutes).
        """
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        recs_count = self.db.query(RecommendationLog).filter(RecommendationLog.created_at >= one_hour_ago).count()
        feedback_count = self.db.query(UserFeedback).filter(UserFeedback.timestamp >= one_hour_ago).count()
        
        return {
            "window_minutes": 60,
            "recommendations_served": recs_count,
            "feedback_received": feedback_count,
            "velocity": round(recs_count / 60, 2)
        }

    def get_strategy_dominance(self):
        """
        Measures which strategies are currently 'winning' the weight battle.
        """
        stats = self.db.query(StrategyStats).order_by(desc(StrategyStats.weight)).all()
        return [
            {
                "strategy": s.strategy_name,
                "global_weight": round(s.weight, 2),
                "total_usage": s.times_used
            }
            for s in stats
        ]

    def get_user_engagement(self):
        """
        Returns a list of users and their engagement scores.
        """
        return get_user_engagement_metrics(self.db)
