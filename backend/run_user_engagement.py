import sqlite3
import os

DB_PATH = "filmBox.db"

QUERY = """
SELECT
    user_id,
    COUNT(*) AS total_recommendations,
    (
        SELECT COUNT(*)
        FROM user_feedback uf
        WHERE uf.user_id = rl.user_id
          AND uf.liked = 1
    ) AS total_likes
FROM recommendation_logs rl
GROUP BY user_id;
"""

def run_analysis():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- User Engagement Analysis (Phase 12.3) ---")
    print(f"{'User ID':<10} | {'Recs Served':<12} | {'Likes':<5} | {'Personalization Score'}")
    print("-" * 65)
    
    try:
        cursor.execute(QUERY)
        results = cursor.fetchall()
        
        if not results:
            print("No data found.")
        
        for row in results:
            user_id, total_recs, total_likes = row
            score = total_likes / total_recs if total_recs > 0 else 0
            print(f"{user_id:<10} | {total_recs:<12} | {total_likes:<5} | {score:.2f}")
            
    except Exception as e:
        print(f"Query Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_analysis()
