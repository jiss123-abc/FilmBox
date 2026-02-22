import os
from dotenv import load_dotenv

load_dotenv(override=True)

ENV = os.getenv("ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./filmBox.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
