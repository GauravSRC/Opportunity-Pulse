"""FastAPI application entrypoint.

Run: ``uvicorn app.main:app --reload`` (from the ``backend/`` directory).
Docs at ``/docs``. Most domain endpoints are Phase-0 stubs returning 501 with a
``TODO(phase-N)`` detail; liveness/readiness work today.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()
log = get_logger(__name__)

# ── Prometheus metrics ────────────────────────────────────────────────────────
_prometheus_available = False
if settings.prometheus_enabled:
    try:
        import time

        from prometheus_client import (
            CONTENT_TYPE_LATEST,
            Counter,
            Histogram,
            generate_latest,
        )
        from starlette.middleware.base import BaseHTTPMiddleware

        REQUEST_COUNT = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
        )
        REQUEST_LATENCY = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "endpoint"],
        )

        class _MetricsMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                start = time.perf_counter()
                response = await call_next(request)
                duration = time.perf_counter() - start
                endpoint = request.url.path
                REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
                REQUEST_LATENCY.labels(request.method, endpoint).observe(duration)
                return response

        _prometheus_available = True
    except ImportError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log.info("startup", app_env=settings.app_env)
    yield
    log.info("shutdown")


app = FastAPI(
    title="OpportunityPulse API",
    version="0.1.0",
    description="Multi-agent opportunity discovery, ranking, and outreach.",
    lifespan=lifespan,
)

if _prometheus_available:
    app.add_middleware(_MetricsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/healthz", tags=["meta"])
def healthz() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/readyz", tags=["meta"])
def readyz() -> dict:
    """Readiness probe."""
    return {"status": "ready"}


@app.get("/metrics", tags=["meta"], include_in_schema=False)
def metrics() -> Response:
    """Prometheus scrape endpoint. Returns 503 if prometheus_client not installed."""
    if not _prometheus_available:
        return Response(content="prometheus_client not available", status_code=503)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
