from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import ENV
from app.core.database import Base, engine

# Auto-create tables (Legacy support)
# In true production, use Alembic migrations instead
import app.models.base_models
import app.models.feedback_models
import app.models.recommendation_log
import app.models.strategy_stats
import app.models.user_strategy_stats

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FilmBox API",
    description="AI-powered movie recommendation system",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": ENV
    }
