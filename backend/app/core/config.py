from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FilmBox Backend"
    DATABASE_URL: str = "sqlite:///./filmBox.db"

settings = Settings()
