"""
Phase 23: Prometheus Metrics & Monitoring Middleware
Tracks request count, latency, error rate, and active requests.
"""
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ─── Prometheus Metrics ───────────────────────────────────────
REQUEST_COUNT = Counter(
    "filmbox_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "filmbox_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ERROR_COUNT = Counter(
    "filmbox_errors_total",
    "Total error responses (4xx/5xx)",
    ["method", "endpoint", "status_code"]
)

ACTIVE_REQUESTS = Gauge(
    "filmbox_active_requests",
    "Number of requests currently being processed"
)

RECOMMENDATION_COUNT = Counter(
    "filmbox_recommendations_served",
    "Total recommendations served",
    ["strategy"]
)

LLM_CALLS = Counter(
    "filmbox_llm_calls_total",
    "Total LLM (Gemini) API calls",
    ["status"]
)


# ─── Middleware ───────────────────────────────────────────────
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        method = request.method
        endpoint = request.url.path
        start_time = time.time()

        try:
            response = await call_next(request)
            status = str(response.status_code)
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status).inc()
            
            if response.status_code >= 400:
                ERROR_COUNT.labels(method=method, endpoint=endpoint, status_code=status).inc()

            return response
        except Exception as e:
            ERROR_COUNT.labels(method=method, endpoint=endpoint, status_code="500").inc()
            raise e
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            ACTIVE_REQUESTS.dec()


def metrics_response():
    """Generate Prometheus metrics output."""
    return Response(
        content=generate_latest(),
        media_type="text/plain; charset=utf-8"
    )
