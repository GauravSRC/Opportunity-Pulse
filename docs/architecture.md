# Architecture notes (supplement)

The primary system map is in the root [`ARCHITECTURE.md`](../ARCHITECTURE.md).
This file holds the deeper rationale and swap-out notes.

## Worker: Arq (default) vs Celery

**Default: Arq.** It is asyncio-native (matches FastAPI and our async HTTP
adapters), tiny, and Redis-only — no extra broker. Job definitions live in
[`worker/arq_app.py`](../worker/arq_app.py).

**When to swap to Celery:** if we need a mature result backend, complex routing,
beat-style cron with many schedules, or a non-Redis broker (RabbitMQ). The task
functions in [`worker/tasks/`](../worker/tasks/) are written as plain async
functions that take their own dependencies, so moving them under Celery means
re-registering them — not rewriting logic.

## Why one Postgres for relational + vectors

Running pgvector inside the same Postgres avoids operating a second system
(e.g., a standalone FAISS service) in the cloud, keeps transactions consistent
(a listing and its embedding commit together), and is plenty fast with an HNSW
index at our scale. FAISS remains an optional **local** fast path for large
offline experiments; it is not required in production.

## Caching layers (Redis)

- HTTP conditional-GET state (ETag / Last-Modified) per source URL.
- Content fingerprints for idempotent ingestion.
- RAG context per listing (outreach).
- Embedding cache keyed by content hash.
- Arq job queue.

## Scheduling

Discovery runs on a schedule (cron via Arq/host scheduler). Each run is
idempotent; re-processing unchanged content is a no-op thanks to fingerprints.

## Security & privacy boundaries

- Résumé blobs live in object storage, encrypted at rest; only a reference is in
  Postgres.
- JWT/OAuth at the API edge; admin routes gated by role.
- Audit log for sensitive actions.
- Data export/delete endpoints for user data rights.

## Deployment topology

Containers: `backend`, `worker`, `web`, plus managed `postgres` (pgvector) and
`redis`. Built and pushed by `.github/workflows/ci.yml`, deployed by
`deploy.yml` to a Fly.io/Render/Railway-class host. See [`../infra/`](../infra/).
