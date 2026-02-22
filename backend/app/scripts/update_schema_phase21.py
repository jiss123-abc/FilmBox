from app.core.database import SessionLocal, engine
from sqlalchemy import text

def add_movie_ids_column():
    session = SessionLocal()
    try:
        # Check if column exists
        result = session.execute(text("PRAGMA table_info(recommendation_logs)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "movie_ids" not in columns:
            print("Adding movie_ids column to recommendation_logs...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE recommendation_logs ADD COLUMN movie_ids TEXT"))
            print("Column added successfully.")
        else:
            print("Column movie_ids already exists.")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    add_movie_ids_column()
