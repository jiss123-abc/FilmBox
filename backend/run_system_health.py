import sqlite3
import os

DB_PATH = "filmBox.db"

QUERY = """
SELECT
    strategy,
    COUNT(*) AS usage_count
FROM recommendation_logs
GROUP BY strategy;
"""

def run_analysis():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- System Health: Strategy Distribution (Phase 12.4) ---")
    print(f"{'Strategy':<25} | {'Usage Count':<12}")
    print("-" * 40)
    
    try:
        cursor.execute(QUERY)
        results = cursor.fetchall()
        
        if not results:
            print("No data found.")
        
        for row in results:
            strategy, count = row
            print(f"{strategy:<25} | {count:<12}")
            
    except Exception as e:
        print(f"Query Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_analysis()
