# Backend (FastAPI) image. Build context = repo root.
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg / build.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps from the shared pyproject (without the heavy scraping extra).
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install ".[dev]"

# App code (shared packages + backend).
COPY backend ./backend
COPY agents ./agents
COPY ranking ./ranking
COPY dedup ./dedup
COPY deadline_parser ./deadline_parser
COPY email_agent ./email_agent
COPY ingestion ./ingestion

# PYTHONPATH mirrors the worker: repo root (top-level packages) + backend (app.*)
ENV PYTHONPATH=/app:/app/backend

WORKDIR /app/backend
EXPOSE 8000
# Shell form so ${PORT} expands (Render assigns a dynamic port; defaults to 8000
# locally). Apply DB migrations first — idempotent, a no-op when already current.
# NOTE: docker-compose overrides this CMD with a --reload command and runs
# migrations separately (see README); this default is what production uses.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
