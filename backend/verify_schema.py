import sqlite3

def verify_schema():
    conn = sqlite3.connect("filmBox.db")
    cursor = conn.cursor()
    
    # 1. List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables in database:", tables)
    
    # 2. Schema for user_feedback
    if 'user_feedback' in tables:
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_feedback';")
        schema = cursor.fetchone()[0]
        print("\nSchema for user_feedback:")
        print(schema)
    else:
        print("\nuser_feedback table NOT FOUND")
        
    conn.close()

if __name__ == "__main__":
    verify_schema()
