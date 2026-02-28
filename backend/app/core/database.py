import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base

# Auto-seed the persistent database on Render
if DATABASE_URL.startswith("sqlite:////data/"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    source_db = os.path.join(os.getcwd(), "filmBox.db")
    if not os.path.exists(db_path):
        print(f"Persistent DB not found at {db_path}. Copying from {source_db}...")
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            shutil.copy2(source_db, db_path)
            print("Successfully seeded the persistent database.")
        except Exception as e:
            print(f"Warning: Failed to seed DB: {e}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # required for SQLite
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
