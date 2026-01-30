import sqlite3
import pandas as pd

def run_analysis():
    conn = sqlite3.connect('filmBox.db')
    
    query = """
    SELECT
        r.strategy,
        COUNT(f.id) AS impressions,
        SUM(case when f.liked = 1 then 1 else 0 end) AS likes,
        ROUND(1.0 * SUM(case when f.liked = 1 then 1 else 0 end) / COUNT(f.id), 3) AS ctr
    FROM recommendation_logs r
    LEFT JOIN user_feedback f ON r.user_id = f.user_id
    WHERE r.experiment_group = 'phase14_ab'
    GROUP BY r.strategy;
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("\n--- Strategy A/B Test Results (phase14_ab) ---")
    if df.empty:
        print("No data recorded for this experiment yet.")
    else:
        print(df.to_string(index=False))
        
        print("\n--- Stopping Rule Check ---")
        for _, row in df.iterrows():
            interaction_status = "✅ OK" if row['impressions'] >= 100 else "🕒 Gathering Data (< 100)"
            print(f"Strategy {row['strategy']}: {interaction_status}")
            
    conn.close()

if __name__ == "__main__":
    run_analysis()
