from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.feedback_models import UserFeedback
from app.models.recommendation_log import RecommendationLog
from app.services.engagement_service import EngagementService

def verify_churn_detection():
    print("--- 🚨 Phase 18: Churn & Disengagement Verification ---")
    db = SessionLocal()
    
    # 1. Cleanup
    db.query(UserFeedback).filter(UserFeedback.user_id.in_(["100", "200", "300"])).delete()
    db.query(RecommendationLog).filter(RecommendationLog.user_id.in_([100, 200, 300])).delete()
    db.commit()

    now = datetime.utcnow()

    # User 100: Healthy (Low Risk)
    print("\nSimulating User 100 (Healthy)...")
    for i in range(5):
        log = RecommendationLog(user_id="100", strategy="collaborative-filtering", created_at=now - timedelta(hours=i), num_recommendations=10)
        db.add(log)
    for i in range(4): # 80% CTR
        fb = UserFeedback(user_id="100", movie_id=i, liked=1, strategy="collaborative-filtering", timestamp=now - timedelta(minutes=10*i))
        db.add(fb)
    
    # User 200: Struggling (Medium Risk)
    print("Simulating User 200 (Medium Risk: Low Likes)...")
    for i in range(5):
        log = RecommendationLog(user_id="200", strategy="popularity-based", created_at=now - timedelta(hours=i), num_recommendations=10)
        db.add(log)
    for i in range(5): # 100% CTR but ALL DISLIKES
        fb = UserFeedback(user_id="200", movie_id=i+10, liked=0, strategy="popularity-based", timestamp=now - timedelta(minutes=10*i))
        db.add(fb)
        
    # User 300: Inactive (High Risk)
    print("Simulating User 300 (High Risk: Inactivity)...")
    # Last log 15 days ago
    last_week = now - timedelta(days=15)
    log = RecommendationLog(user_id="300", strategy="content-based", created_at=last_week, num_recommendations=10)
    db.add(log)
    fb = UserFeedback(user_id="300", movie_id=99, liked=1, strategy="content-based", timestamp=last_week)
    db.add(fb)
    
    db.commit()

    # Verify Logic
    service = EngagementService(db)
    
    users = ["100", "200", "300"]
    expected_risks = {"100": "LOW", "200": "MEDIUM", "300": "HIGH"}
    
    for uid in users:
        risk = service.get_churn_risk(uid)
        score = service.calculate_engagement_score(uid)
        print(f"User {uid}: Risk={risk} | Score={score:.2f}")
        
    print("\n✅ Verification data generated. Check /api/admin/analytics/churn for results.")
    db.close()

if __name__ == "__main__":
    verify_churn_detection()
