from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

from app.api.health import router as health_router
from app.api import recommendations
from app.api import content_recommendations
from app.api import hybrid_recommendations
from app.api.agent import router as agent_router
from app.api.conversational_agent import router as conversational_router
from app.api.conversational_agent_api import router as llm_router
from app.api.feedback_api import router as feedback_router
from app.api.admin_api import router as admin_router
from app.api.admin_analytics import router as admin_analytics_router
from app.core.database import Base, engine
import app.models.base_models
import app.models.feedback_models
import app.models.recommendation_log
import app.models.strategy_stats
import app.models.user_strategy_stats

app = FastAPI(title="FilmBox Backend")

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(
    content_recommendations.router,
    prefix="/api",
    tags=["Content-Based Recommendations"]
)
app.include_router(
    hybrid_recommendations.router,
    prefix="/api",
    tags=["Hybrid Recommendations"]
)
app.include_router(agent_router)
app.include_router(conversational_router)
app.include_router(llm_router)
app.include_router(feedback_router)
app.include_router(admin_router)
app.include_router(admin_analytics_router)

# Create tables in SQLite automatically
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "FilmBox backend is running"}
