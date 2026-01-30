import sqlite3
import os
import argparse

DB_PATH = "filmBox.db"

def debug_user(user_id):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"=== Debugging User Flow: ID {user_id} ===")
    
    # 1. Last Decision
    print("\n[1] Last Recommendation Decision:")
    cursor.execute("""
        SELECT strategy, num_recommendations, created_at
        FROM recommendation_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1;
    """, (user_id,))
    last_rec = cursor.fetchone()
    if last_rec:
        print(f"Strategy: {last_rec[0]}")
        print(f"Items:    {last_rec[1]}")
        print(f"Time:     {last_rec[2]}")
    else:
        print("No recommendation logs found for this user.")

    # 2. Feedback History
    print("\n[2] Feedback History:")
    cursor.execute("""
        SELECT movie_id, liked, rating, timestamp
        FROM user_feedback
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5;
    """, (str(user_id),))
    feedbacks = cursor.fetchall()
    if feedbacks:
        print(f"{'Movie ID':<10} | {'Liked':<5} | {'Rating':<6} | {'Timestamp'}")
        print("-" * 50)
        for fb in feedbacks:
            movie_id, liked, rating, timestamp = fb
            liked_str = str(liked) if liked is not None else "N/A"
            rating_str = f"{rating:.1f}" if rating is not None else "N/A"
            print(f"{movie_id:<10} | {liked_str:<5} | {rating_str:<6} | {timestamp}")
    else:
        print("No feedback found for this user.")

    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug user recommendation flow")
    parser.add_argument("--user", type=int, default=42, help="User ID to debug (default: 42)")
    args = parser.parse_args()
    debug_user(args.user)
