# Worker (Arq) image. Build context = repo root.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install "."

# Shared packages used by the pipelines.
COPY backend ./backend
COPY worker ./worker
COPY agents ./agents
COPY ranking ./ranking
COPY dedup ./dedup
COPY deadline_parser ./deadline_parser
COPY email_agent ./email_agent
COPY ingestion ./ingestion

# PYTHONPATH includes repo root (top-level packages) and backend (app.*).
ENV PYTHONPATH=/app:/app/backend
CMD ["arq", "worker.arq_app.WorkerSettings"]
