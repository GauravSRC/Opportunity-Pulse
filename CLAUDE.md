# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## What this project is

**OpportunityPulse** is a multi-agent, real-time opportunity discovery platform.
It continuously finds, deduplicates, ranks, and explains opportunities (jobs,
internships, research/lab roles, fellowships, hackathons, grants, conferences,
GSoC-like programs) from 30+ web sources, extracts messy deadlines, models
urgency/decay, and drafts the **right outreach artifact per opportunity type**
(cold email *only* for professor/lab roles; cover letter / SOP / team pitch /
proposal otherwise).

Read [`PROJECT.md`](PROJECT.md) for the full end-to-end design and
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the system map. Deep-dives live in
[`docs/`](docs/).

> **Status:** Complete. All core services, API routers, worker tasks, frontend
> pages, Chrome extension, Prometheus metrics, and Docker images are implemented
> and working. The full pipeline runs end-to-end: ingest → normalize → dedup →
> embed → deadline extraction → ranking → outreach generation. 41 tests pass on
> SQLite in-memory. `docker compose up --build` starts all 5 containers healthy.
> Run `python -m pytest backend/tests/ tests/ -q` from the repo root.

## Repository layout

```
backend/          FastAPI sync API — all routers wired to service layer
  app/api/        profiles, opportunities, outreach, deadlines, feedback,
                  alerts, sources, admin — no 501 stubs remain
  app/services/   pipeline, ranking_service, outreach_service,
                  feedback_service, profile_service, source_service
  app/models/     SQLAlchemy ORM (portable GUID/JSON/array/vector types)
  tests/          SQLite in-memory integration tests (41 passing)
worker/           Arq async workers — all 7 tasks wired to service layer
  tasks/          ingest (run_source per enabled source), normalize (recovery),
                  dedup (dedup_all), rank (rank_user, batch), deadline
                  (extract missing deadlines), decay (exponential urgency),
                  alerts (score≥65% + deadline≤7d → Alert rows)
  arq_app.py      Cron: discovery every 30 min, dedup/decay/deadline hourly,
                  alerts every 15 min; RedisSettings from REDIS_URL
agents/           LangGraph orchestration (graphs/, nodes/, state.py, llm.py)
ingestion/        Source adapters + registry + rate limit
  sources/        demo_fixture (✓ offline), greenhouse, lever, remotive,
                  github, arxiv, rss_generic, kaggle + more stubs
  fixtures/       sample_opportunities.json (10 diverse demo listings)
ranking/          Embedder (hashing default + sentence-transformers swap),
                  retriever, scorer (blend + explanation), features, learning
dedup/            Blocker, similarity (cosine + rapidfuzz), cluster, merge
deadline_parser/  Rules → relative → NER → LLM fallback ladder
email_agent/      Type-routed router, RAG, generators (6 artifact types)
models/           ML model cards / configs
evaluation/       Offline + online eval harness and datasets
web/              Next.js App Router — all pages functional
  app/onboarding  3-step profile creation form → POST /profiles
  app/feed        Ranked feed, search, type/remote filters, pagination,
                  feedback buttons
  app/opportunity/[id]  Detail + "Why it matched" score breakdown panel
  app/outreach/[id]     Type-routed draft editor (never auto-sent)
  app/deadlines   Urgency-sorted tracker + .ics calendar export
  app/settings    Profile edit (skills, intents, locations)
  components/     OpportunityCard, MatchScoreBadge, DeadlineBadge,
                  WhyMatchedPanel, OutreachPanel, FeedbackButtons
  lib/api.ts      Typed API client covering all backend endpoints
extension/        Chrome MV3 — functional badge + popup
  content/        Injects match-score badge on Greenhouse/Lever/Remotive pages
  popup/          Score lookup, user ID setup, "View in app" action
  background/     Service worker — proxies score requests to backend
infra/            docker/, deploy/ (Fly.io), prometheus/
  docker/         backend.Dockerfile + worker.Dockerfile
                  Both require COPY pyproject.toml README.md ./  (hatchling needs README)
                  Both set ENV PYTHONPATH=/app:/app/backend
scripts/          demo_seed.py (seeds DB + ranks demo user), seed_sources.py
tests/            Cross-service integration tests
docs/             Design deep-dives
```

## Core principles (do not violate)

1. **No Reddit API** and no login-walled or paid-data scraping. Respect
   `robots.txt` and source ToS. Source access fallback ladder:
   **Official API -> ATS JSON -> RSS/Atom -> sitemap.xml -> search API ->
   headless browser (Playwright, last resort).**
2. **Outreach is type-routed.** Cold email is generated **only** for
   research/lab/professor opportunities. Other types get cover letter, SOP,
   team pitch, proposal, or referral note. The router lives in
   [`email_agent/router.py`](email_agent/router.py). Never hardcode "cold email"
   as the default artifact.
3. **Drafts are never auto-sent.** Outreach always passes a human-in-the-loop
   approval gate.
4. **Every ML stage has a deterministic fallback** so the product degrades
   gracefully (e.g., deadline rules-only when the LLM is unavailable; lexical
   search when embeddings fail). Never let a model failure 500 a user request.
5. **Explainability is a feature.** Ranking must emit per-component
   contributions (semantic, skill overlap, recency, urgency, feedback).
6. **LangGraph** owns stateful/branching/retryable/HITL flows. **LangChain** is
   used narrowly (loaders, splitters, retriever wrappers, LLM abstraction) —
   never for plain HTTP/DB calls or the core ranking/dedup/deadline math.

## Tech stack

- Backend: **FastAPI** (Python 3.11+), **SQLAlchemy** + **Alembic**.
- Data: **PostgreSQL + pgvector** (relational + vectors, HNSW index). **Redis**
  (queue + cache).
- Async: **Arq** workers (Celery swap documented in `docs/architecture.md`).
- Agents: **LangGraph**; **LangChain** (narrow use); provider-agnostic LLM layer
  in [`agents/llm.py`](agents/llm.py) over **Claude (default)**, **OpenAI**, and
  **Ollama (local fallback)**.
- ML: **sentence-transformers** (default `BAAI/bge-small-en-v1.5`), optional
  cross-encoder reranker (`cross-encoder/ms-marco-MiniLM-L-6-v2`), `rapidfuzz`,
  `dateparser`, `spaCy`.
- Discovery: **Tavily** (default) / **SerpAPI** behind one interface;
  **Playwright** last resort.
- Web: **Next.js** (App Router). Extension: **Chrome MV3**.
- Observability: **LangSmith** + **Prometheus** (`/metrics` endpoint, `prometheus_client`,
  `_MetricsMiddleware` records request count + latency per path) + structured logs.
- Ops: **Docker** + docker-compose; **GitHub Actions** (CI + deploy to Fly.io).

## Common commands

```bash
# Install Python dependencies (from repo root)
pip install -e ".[dev]"

# Bring up infra (Postgres+pgvector, Redis)
docker compose up -d db redis

# Full stack (all 5 containers: db, redis, backend, worker, web)
docker compose up --build

# Backend (from backend/)
uvicorn app.main:app --reload          # dev server -> http://localhost:8000/docs
alembic upgrade head                   # apply migrations (requires Postgres)

# Tests — all 41 pass on SQLite in-memory, no Postgres needed
python -m pytest backend/tests/ tests/ -q

# Seed demo data (from repo root; requires running backend DB)
python scripts/demo_seed.py

# Worker (from repo root)
arq worker.arq_app.WorkerSettings

# Web (from web/)
npm install && npm run dev             # -> http://localhost:3000

# Chrome extension — load unpacked from extension/ in chrome://extensions

# Lint / format (Python)
ruff check . && ruff format .

# Deploy to Fly.io
fly deploy --config infra/deploy/fly.toml
fly status --config infra/deploy/fly.toml   # shows live URL
```

## Key API endpoints

```
POST   /profiles                       Create user + profile
GET    /profiles/{id}                  Get profile
PATCH  /profiles/{id}                  Update profile
POST   /profiles/{id}/resume           Upload résumé (text extraction)

GET    /opportunities                  Search/feed (query params: q, type, remote, user_id)
GET    /opportunities/{id}             Opportunity detail
GET    /opportunities/{id}/explanation Ranking explanation (components breakdown)
POST   /opportunities/{id}/score       Ad hoc match score (extension use)

POST   /opportunities/{id}/outreach    Generate type-routed draft (cold email / cover letter / SOP / ...)
PATCH  /outreach/{id}                  Edit / approve draft

POST   /deadlines/extract              Ad hoc deadline extraction from text

POST   /feedback                       Submit implicit/explicit feedback signal

GET    /alerts                         List alerts
POST   /alerts                         Create alert rule
PATCH  /alerts/{id}                    Update alert

GET    /sources                        List ingestion sources
POST   /sources/sync                   Sync registry.yaml → DB
POST   /sources/{key}/ingest           Trigger ingest for one source
POST   /sources/ingest-all             Ingest all enabled sources
POST   /sources/dedup                  Run deduplication pass
POST   /admin/rank/{user_id}           Recompute rank scores for user
GET    /admin/health                   Source health + pipeline status

GET    /metrics                        Prometheus scrape endpoint (text/plain 0.0.4)
GET    /healthz                        Liveness probe
GET    /readyz                         Readiness probe
```

## Embedding providers

Set `EMBEDDING_PROVIDER` in `.env`:
- `hashing` (default, zero dependencies): deterministic feature-hashing, always works.
- `local`: uses `sentence-transformers` (requires `pip install sentence-transformers`).
- `openai`: uses OpenAI embeddings API (requires `OPENAI_API_KEY`).

## LLM providers

Set `LLM_PROVIDER` in `.env` (`anthropic` | `openai` | `ollama`). If unset,
LLM-dependent stages (deadline LLM fallback, outreach RAG) degrade gracefully
to deterministic paths.

## Environment

Copy `.env.example` to `.env` and fill in keys. The user has access to:
Anthropic, OpenAI, a web-search API (Tavily/SerpAPI), GitHub token, Kaggle
token+username. Local models via Ollama are the zero-cost fallback. **Never**
commit `.env` or real secrets; `.gitignore` excludes them.

## Docker image notes

Both `backend.Dockerfile` and `worker.Dockerfile` share two requirements that
are easy to break:

1. **`COPY pyproject.toml README.md ./` before `pip install`** — hatchling reads
   `readme = "README.md"` from `pyproject.toml` during the build step and raises
   `OSError: Readme file does not exist` if README.md is not present.
2. **`ENV PYTHONPATH=/app:/app/backend`** — top-level packages (`agents`,
   `ranking`, `dedup`, `deadline_parser`, `email_agent`, `ingestion`) live under
   `/app`; the FastAPI `app` package lives under `/app/backend`. Both paths must
   be on `PYTHONPATH` or imports fail at container startup.

## Conventions

- Python: type hints everywhere, `ruff` for lint+format, `pydantic` for I/O
  schemas, snake_case modules.
- Each ingestion source is a thin adapter subclassing the base in
  [`ingestion/sources/base.py`](ingestion/sources/base.py) and registered in
  [`ingestion/registry.yaml`](ingestion/registry.yaml). Adapters must be
  schema-tolerant (never assume a field exists) and emit the canonical
  `NormalizedListing`.
- DB portability: use `GUID()`, `json_type()`, `str_array()`, `vector_type()`
  from [`backend/app/db/types.py`](backend/app/db/types.py) — never raw
  `UUID`, `JSONB`, `ARRAY`, or `pgvector.Vector` in model files.
- New work should be tagged with `TODO(phase-N)` so the roadmap stays legible.
- Tests use SQLite in-memory (no Postgres needed). `conftest.py` overrides
  `get_db` with a transactional test session that rolls back after each test.
- Frontend pages are all `"use client"` with `useEffect` fetch — no server
  components hitting the API directly (keeps CORS simple for local dev).
- The `userId` / `profileId` from onboarding are stored in `localStorage` and
  passed as query params to personalize the feed and explanation endpoints.

## Where to start reading code

`backend/app/main.py` → `backend/app/api/` (routers) → `backend/app/services/`
(business logic) → `backend/app/models/` (ORM schema) →
`ingestion/sources/base.py` (adapter contract) →
`ranking/scorer.py` (score blend + explanation) →
`email_agent/router.py` (outreach type routing) →
`web/app/feed/page.tsx` (frontend entry point).
