from fastapi import APIRouter

# Import logic routers
from app.api.health import router as health_router
from app.api.recommendations import router as rec_router
from app.api.content_recommendations import router as content_rec_router
from app.api.hybrid_recommendations import router as hybrid_rec_router
from app.api.conversational_agent_api import router as agent_router
from app.api.feedback_api import router as feedback_router
from app.api.admin_api import router as admin_router
from app.api.admin_analytics import router as admin_analytics_router
from app.api.tmdb_enrichment_api import router as tmdb_enrichment_router  # TEMP: remove after enrichment
from app.api.movie_search_api import router as movie_search_router

api_router = APIRouter()

# Register routes
api_router.include_router(health_router, prefix="/api", tags=["Health"])
api_router.include_router(rec_router, prefix="/api", tags=["Recommendations"])
api_router.include_router(content_rec_router, prefix="/api", tags=["Content Recommendations"])
api_router.include_router(hybrid_rec_router, prefix="/api", tags=["Hybrid Recommendations"])
api_router.include_router(agent_router, tags=["AI Agent"])
api_router.include_router(feedback_router, tags=["Feedback"])
api_router.include_router(admin_router, tags=["Admin"])
api_router.include_router(admin_analytics_router, tags=["Admin Analytics"])
api_router.include_router(tmdb_enrichment_router, tags=["TMDb Enrichment"])  # TEMP: remove after enrichment
api_router.include_router(movie_search_router, tags=["Movie Search"])
