import os
import logging
from fastapi import FastAPI
from fastapi.responses import Response

from app.api.router import api_router
from app.core.config import ENV, LOG_LEVEL
from app.core.database import Base, engine, SessionLocal
from app.core.monitoring import MetricsMiddleware, metrics_response
from app.core.logging_config import setup_logging

# ─── Phase 23: Structured Logging ────────────────────────────
logger = setup_logging(level=LOG_LEVEL)

# ─── Phase 23: Sentry Error Tracking ─────────────────────────
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=0.3,
            environment=ENV
        )
        logger.info("✅ Sentry initialized successfully")
    except ImportError:
        logger.warning("⚠️ sentry-sdk not installed, error tracking disabled")
else:
    logger.info("ℹ️ SENTRY_DSN not set, error tracking disabled")

# ─── Database Setup ──────────────────────────────────────────
import app.models.base_models
import app.models.feedback_models
import app.models.recommendation_log
import app.models.strategy_stats
import app.models.user_strategy_stats

Base.metadata.create_all(bind=engine)

# ─── App ─────────────────────────────────────────────────────
app = FastAPI(
    title="FilmBox API",
    description="AI-powered movie recommendation system",
    version="1.0.0"
)

# Phase 23: Add Prometheus metrics middleware
app.add_middleware(MetricsMiddleware)

app.include_router(api_router)

# ─── Phase 23: Prometheus Metrics Endpoint ────────────────────
@app.get("/metrics", include_in_schema=False)
def prometheus_metrics():
    return metrics_response()

# ─── Phase 23: Enhanced Health Check ─────────────────────────
@app.get("/health")
def health_check():
    health = {
        "status": "ok",
        "environment": ENV,
        "version": "1.0.0",
        "checks": {}
    }

    # DB connectivity check
    try:
        db = SessionLocal()
        db.execute(db.bind.raw_connection().cursor().execute("SELECT 1") or "SELECT 1")
        db.close()
        health["checks"]["database"] = "connected"
    except Exception:
        try:
            db = SessionLocal()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
            health["checks"]["database"] = "connected"
        except Exception as e:
            health["checks"]["database"] = f"error: {str(e)}"
            health["status"] = "degraded"

    # Gemini API check
    gemini_enabled = os.getenv("ENABLE_LLM", "false").lower() == "true"
    health["checks"]["gemini_llm"] = "enabled" if gemini_enabled else "disabled"

    # Sentry check
    health["checks"]["error_tracking"] = "active" if SENTRY_DSN else "inactive"

    return health
