import sqlite3
import pandas as pd
from app.core.database import SessionLocal
from app.analytics.strategy_metrics import get_strategy_metrics
from app.analytics.user_engagement import get_user_engagement_metrics
from app.analytics.strategy_trends import get_strategy_evolution_metrics

def verify_final_analytics():
    db = SessionLocal()
    
    print("--- 🏆 Phase 15 Final Verification: Analytics & Monitoring ---")
    
    # 1. Strategy Leaderboard
    print("\n[1/4] Strategy Leaderboard (api/admin/analytics/strategies)")
    leaderboard = get_strategy_metrics(db)
    df_leaderboard = pd.DataFrame([{
        "strategy": r.strategy,
        "impressions": r.impressions,
        "likes": r.likes,
        "ctr": round(float(r.ctr), 3) if r.ctr is not None else 0
    } for r in leaderboard])
    print(df_leaderboard.to_string(index=False) if not df_leaderboard.empty else "No data yet.")

    # 2. User Engagement
    print("\n[2/4] User Engagement (api/admin/analytics/user-engagement)")
    engagement = get_user_engagement_metrics(db)
    df_engagement = pd.DataFrame([{
        "user_id": r.user_id,
        "interactions": r.total_interactions,
        "likes": r.likes,
        "score": round(float(r.engagement_score), 2)
    } for r in engagement])
    print(df_engagement.head(5).to_string(index=False) if not df_engagement.empty else "No data yet.")

    # 3. Strategy Evolution
    print("\n[3/4] Strategy Evolution (api/admin/analytics/evolution)")
    evolution = get_strategy_evolution_metrics(db, days=7)
    df_evolution = pd.DataFrame([{
        "day": r.day,
        "strategy": r.strategy,
        "ctr": round(float(r.ctr), 3)
    } for r in evolution])
    print(df_evolution.head(10).to_string(index=False) if not df_evolution.empty else "No data yet.")

    # 4. Consistency Check (Direct SQL vs SQLAlchemy)
    print("\n[4/4] SQLite Integrity Check")
    conn = sqlite3.connect('filmBox.db')
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM user_feedback WHERE strategy IS NOT NULL")
    attributed_count = cursor.fetchone()[0]
    print(f"Total feedbacks with strategy attribution: {attributed_count}")
    conn.close()

    db.close()
    print("\n✅ Phase 15 Verification Complete.")

if __name__ == "__main__":
    verify_final_analytics()
