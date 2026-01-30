import sqlite3
import os

DB_PATH = "filmBox.db"

QUERY = """
SELECT
    r.strategy,
    COUNT(f.id) AS total_feedback,
    SUM(CASE WHEN f.liked = 1 THEN 1 ELSE 0 END) AS positive_feedback,
    ROUND(
        CAST(SUM(CASE WHEN f.liked = 1 THEN 1 ELSE 0 END) AS FLOAT)
        / COUNT(f.id),
        2
    ) AS success_rate
FROM recommendation_logs r
JOIN user_feedback f
  ON r.user_id = f.user_id
GROUP BY r.strategy;
"""

def run_analysis():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Strategy Performance Evaluation (Phase 12.2) ---")
    print(f"{'Strategy':<25} | {'Feedback':<8} | {'Likes':<5} | {'Success Rate'}")
    print("-" * 60)
    
    try:
        cursor.execute(QUERY)
        results = cursor.fetchall()
        
        if not results:
            print("No data found. (Ensure you have both recommendation_logs and user_feedback for the same users)")
        
        for row in results:
            strategy, total, positive, rate = row
            print(f"{strategy:<25} | {total:<8} | {positive:<5} | {rate:.2f}")
            
    except Exception as e:
        print(f"Query Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_analysis()
