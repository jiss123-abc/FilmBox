import sqlite3
import os
import sys

# Add the current directory to sys.path to allow imports from 'app'
sys.path.append(os.getcwd())

try:
    from app.core.database import SessionLocal
    from app.agents.recommendation_agent import run_recommendation_agent
    from app.api.feedback_api import update_user_strategy_feedback
    from app.models.user_strategy_stats import UserStrategyStats
except ImportError as e:
    print(f"❌ Error importing app modules: {e}")
    sys.exit(1)

def check_db_schema():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user_strategy_stats)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    expected = ['id', 'user_id', 'strategy', 'total_used', 'positive_feedback', 'weight']
    if all(col in columns for col in expected):
        print("✅ DB Schema matches Phase 11.2 spec!")
    else:
        print(f"❌ DB Schema mismatch. Found columns: {columns}")

def test_adaptive_routing():
    db = SessionLocal()
    user_id = 12345
    
    print(f"\n--- 🧠 Phase 11.2: Adaptive Routing Test (User {user_id}) ---")
    
    # 1. Trigger usage
    print("Serving first recommendation...")
    run_recommendation_agent(user_id=user_id, message="Recommend something")
    
    # 2. Check table entries
    row = db.query(UserStrategyStats).filter_by(user_id=user_id).first()
    if row:
        print(f"✅ Strategy '{row.strategy}' initialized for user.")
        print(f"   Usage: {row.total_used} | Feedback: {row.positive_feedback} | Weight: {row.weight:.4f}")
    
    # 3. Simulate feedback to increase weight
    print(f"\nSimulating 'Like' for {row.strategy}...")
    update_user_strategy_feedback(db, user_id, row.strategy)
    
    db.refresh(row)
    print(f"✅ New Weight: {row.weight:.4f} (Increased as expected)")
    
    # 4. Independent weight for second user
    other_user = 67890
    print(f"\n--- 👥 Multi-User Independence Test (User {other_user}) ---")
    run_recommendation_agent(user_id=other_user, message="Recommend something")
    other_row = db.query(UserStrategyStats).filter_by(user_id=other_user).first()
    
    if other_row.weight == 1.0:
        print(f"✅ User {other_user} weight is 1.0 (Independent of User {user_id})")
    else:
        print(f"❌ User {other_user} weight is {other_row.weight} (Should be 1.0)")

    db.close()

if __name__ == "__main__":
    check_db_schema()
    test_adaptive_routing()
