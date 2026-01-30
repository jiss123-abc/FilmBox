from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models.recommendation_log import RecommendationLog
from app.models.feedback_models import UserFeedback
from app.models.strategy_stats import StrategyStats
from app.analytics.user_engagement import get_user_engagement_metrics
from app.analytics.strategy_trends import get_strategy_evolution_metrics
from app.services.engagement_service import EngagementService

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

    def get_churn_analysis(self):
        """
        Returns a summary of churn risks across the user base.
        """
        engagement_service = EngagementService(self.db)
        
        # Get all active user IDs from feedback or logs
        user_ids_query = self.db.query(UserFeedback.user_id).distinct().all()
        user_ids = [str(u[0]) for u in user_ids_query]
        
        log_user_ids_query = self.db.query(RecommendationLog.user_id).distinct().all()
        user_ids.extend([str(u[0]) for u in log_user_ids_query])
        
        unique_users = list(set(user_ids))
        
        results = []
        for uid in unique_users:
            risk = engagement_service.get_churn_risk(uid)
            score = engagement_service.calculate_engagement_score(uid)
            results.append({
                "user_id": uid,
                "risk_level": risk,
                "engagement_score": round(score, 2)
            })
            
        return results
