import sqlite3

def run_query_2_1():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        movie_id, 
        COUNT(*) AS likes
    FROM user_feedback
    WHERE liked = 1
    GROUP BY movie_id
    ORDER BY likes DESC
    LIMIT 10;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n📊 2.1 Most Liked Movies")
    print("-" * 30)
    print(f"{'Movie ID':<10} | {'Likes':<5}")
    print("-" * 30)
    
    if not results:
        print("No 'Liked' feedback found yet.")
    else:
        for movie_id, likes in results:
            print(f"{movie_id:<10} | {likes:<5}")
            
    conn.close()

def run_query_2_2():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        movie_id, 
        COUNT(*) AS dislikes
    FROM user_feedback
    WHERE liked = 0
    GROUP BY movie_id
    ORDER BY dislikes DESC
    LIMIT 10;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n📊 2.2 Most Disliked Movies")
    print("-" * 30)
    print(f"{'Movie ID':<10} | {'Dislikes':<5}")
    print("-" * 30)
    
    if not results:
        print("No 'Disliked' feedback found yet.")
    else:
        for movie_id, dislikes in results:
            print(f"{movie_id:<10} | {dislikes:<5}")
            
    conn.close()

def run_query_2_3():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        user_id, 
        COUNT(*) AS total_feedback
    FROM user_feedback
    GROUP BY user_id
    ORDER BY total_feedback DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n👥 2.3 Most Active Users")
    print("-" * 35)
    print(f"{'User ID':<15} | {'Total Feedback':<5}")
    print("-" * 35)
    
    if not results:
        print("No user feedback interaction found yet.")
    else:
        for user_id, total_fb in results:
            print(f"{user_id:<15} | {total_fb:<5}")
            
    conn.close()

def run_query_2_4():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    # Using 'timestamp' as verified in Step 0
    query = """
    SELECT 
        DATE(timestamp) AS day, 
        COUNT(*) AS feedback_count
    FROM user_feedback
    GROUP BY day
    ORDER BY day DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n📈 2.4 Feedback Trend Over Time")
    print("-" * 30)
    print(f"{'Day':<15} | {'Feedback Count':<5}")
    print("-" * 30)
    
    if not results:
        print("No time-based feedback data available.")
    else:
        for day, count in results:
            print(f"{day or 'N/A':<15} | {count:<5}")
            
    conn.close()

def run_query_2_5():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT
        uf.movie_id,
        AVG(r.rating) AS avg_rating,
        SUM(CASE WHEN uf.liked = 1 THEN 1 ELSE 0 END) AS likes
    FROM user_feedback uf
    JOIN ratings r ON uf.movie_id = r.movie_id
    GROUP BY uf.movie_id
    ORDER BY likes DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n⚖️ 2.5 Feedback vs Rating Alignment")
    print("-" * 45)
    print(f"{'Movie ID':<10} | {'Avg Rating':<12} | {'Total Like-Hits':<10}")
    print("-" * 45)
    
    if not results:
        print("No alignment data available (check if ratings exist for liked movies).")
    else:
        for movie_id, avg_r, hits in results:
            print(f"{movie_id:<10} | {avg_r:<12.2f} | {hits:<10}")
            
    conn.close()

def run_query_4_1():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT
        strategy,
        COUNT(*) AS times_used
    FROM recommendation_logs
    GROUP BY strategy
    ORDER BY times_used DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n🤖 4.1 Strategy Usage")
    print("-" * 35)
    print(f"{'Strategy':<25} | {'Times Used':<5}")
    print("-" * 35)
    
    if not results:
        print("No strategy logs found yet. Run a recommendation to generate data!")
    else:
        for strategy, count in results:
            print(f"{strategy:<25} | {count:<5}")
            
    conn.close()

def run_query_4_2():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    query = """
    SELECT
        rl.strategy,
        COUNT(uf.id) AS likes
    FROM recommendation_logs rl
    JOIN user_feedback uf ON rl.user_id = uf.user_id
    WHERE uf.liked = 1
    GROUP BY rl.strategy;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\n🎯 4.2 Strategy Effectiveness (Likes)")
    print("-" * 35)
    print(f"{'Strategy':<25} | {'Total Likes':<5}")
    print("-" * 35)
    
    if not results:
        print("No likes-to-strategy matches yet. Keep collecting feedback!")
    else:
        for strategy, likes in results:
            print(f"{strategy:<25} | {likes:<5}")
            
    conn.close()

if __name__ == "__main__":
    run_query_2_1()
    run_query_2_2()
    run_query_2_3()
    run_query_2_4()
    run_query_2_5()
    run_query_4_1()
    run_query_4_2()
