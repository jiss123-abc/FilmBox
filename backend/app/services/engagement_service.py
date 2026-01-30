from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.feedback_models import UserFeedback
from app.models.recommendation_log import RecommendationLog

class EngagementService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_engagement_score(self, user_id: any, days: int = 14) -> float:
        """
        Calculates an engagement score (0-1) for a user over a given window.
        - High Score (0.8+): Power user.
        - Medium Score (0.4-0.8): Active user.
        - Low Score (<0.4): Risk of churn.
        """
        user_id_str = str(user_id)
        since = datetime.utcnow() - timedelta(days=days)
        
        # 1. Interactions (Likes/Dislikes)
        interactions = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id_str,
            UserFeedback.timestamp >= since
        ).count()
        
        # 2. Impressions (Recommendations served)
        impressions = self.db.query(RecommendationLog).filter(
            RecommendationLog.user_id == user_id_str,
            RecommendationLog.created_at >= since
        ).count()
        
        if impressions == 0:
            return 0.0 # No activity at all
            
        # CTR-based engagement
        ctr = interactions / impressions
        
        # 3. Quality Factor (Likes vs Dislikes)
        likes = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == str(user_id),
            UserFeedback.timestamp >= since,
            UserFeedback.liked == 1
        ).count()
        
        like_ratio = likes / interactions if interactions > 0 else 0
        
        # Weighted Score: 60% CTR, 40% Like Ratio
        score = (ctr * 0.6) + (like_ratio * 0.4)
        return min(1.0, score)

    def get_churn_risk(self, user_id: any) -> str:
        """
        Categorizes churn risk based on engagement score and inactivity.
        """
        user_id_str = str(user_id)
        # 1. Check Last Activity
        last_feedback = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id_str
        ).order_by(UserFeedback.timestamp.desc()).first()
        
        last_log = self.db.query(RecommendationLog).filter(
            RecommendationLog.user_id == user_id_str
        ).order_by(RecommendationLog.created_at.desc()).first()
        
        last_activity = None
        if last_feedback and last_log:
            last_activity = max(last_feedback.timestamp, last_log.created_at)
        elif last_feedback:
            last_activity = last_feedback.timestamp
        elif last_log:
            last_activity = last_log.created_at
            
        if not last_activity:
            return "NEW" # No history yet
            
        days_inactive = (datetime.utcnow() - last_activity).days
        
        # 2. Thresholds
        if days_inactive >= 30:
            return "CRITICAL" # Churned
        if days_inactive >= 14:
            return "HIGH" # High Risk
            
        score = self.calculate_engagement_score(user_id)
        
        if score < 0.2:
            return "HIGH"
        if score < 0.5:
            return "MEDIUM"
            
        return "LOW"
