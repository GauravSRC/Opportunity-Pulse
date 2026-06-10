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
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install ".[dev]"

# App code (shared packages + backend).
COPY backend ./backend
COPY agents ./agents
COPY ranking ./ranking
COPY dedup ./dedup
COPY deadline_parser ./deadline_parser
COPY email_agent ./email_agent
COPY ingestion ./ingestion

WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
