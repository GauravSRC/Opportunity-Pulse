"""FastAPI application entrypoint.

Run: ``uvicorn app.main:app --reload`` (from the ``backend/`` directory).
Docs at ``/docs``. Most domain endpoints are Phase-0 stubs returning 501 with a
``TODO(phase-N)`` detail; liveness/readiness work today.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log.info("startup", app_env=settings.app_env)
    # TODO(phase-1): warm embedding model / verify DB + Redis connectivity.
    yield
    log.info("shutdown")


app = FastAPI(
    title="OpportunityPulse API",
    version="0.1.0",
    description="Multi-agent opportunity discovery, ranking, and outreach.",
    lifespan=lifespan,
)

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
    """Readiness probe.

    TODO(phase-0/7): check DB + Redis connectivity before returning ready.
    """
    return {"status": "ready"}
