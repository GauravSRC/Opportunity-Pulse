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

> **Status:** Phase 0 scaffold. Most Python/TS modules are stubs with
> docstrings, signatures, and `TODO(phase-N)` markers. Config files, the data
> model, and docs are real. Do not assume business logic is implemented yet —
> grep for `TODO(phase-` to find what is intentionally unfinished.

## Repository layout

```
backend/          FastAPI sync API (read/search/draft/feedback)
worker/           Arq async workers (ingest/normalize/dedup/rank/deadline/alerts)
agents/           LangGraph orchestration (graphs/, nodes/, state.py, llm.py)
ingestion/        Source adapters (one per source type) + registry + rate limit
ranking/          Embedding, retrieval, rerank, score blend, explanation
dedup/            Blocking, similarity, clustering, metadata merge
deadline_parser/  Rules -> NER -> LLM fallback ladder + confidence
email_agent/      Type-routed outreach (router.py), RAG, generators, templates
models/           ML model cards / configs / (future) training scripts
evaluation/       Offline + online + human eval harness and datasets
web/              Next.js app (onboarding, feed, detail, deadline tracker, ...)
extension/        Chrome MV3 (content badge + popup)
infra/            docker/, deploy/ (Fly.io etc.), prometheus/
scripts/          Dev/ops scripts
tests/            Cross-service tests
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
- Observability: **LangSmith** + OpenTelemetry/Prometheus + structured logs.
- Ops: **Docker** + docker-compose; **GitHub Actions** (CI + deploy to Fly.io).

## Common commands

> These describe the intended workflow. In the Phase 0 scaffold some will only
> bring up infra or collect placeholder tests until later phases land.

```bash
# Bring up infra (Postgres+pgvector, Redis)
docker compose up -d db redis

# Validate compose file without starting anything
docker compose config

# Full stack
docker compose up --build

# Backend (from backend/)
uvicorn app.main:app --reload          # dev server -> http://localhost:8000/docs
alembic upgrade head                   # apply migrations
pytest                                 # run tests

# Worker (from repo root)
arq worker.arq_app.WorkerSettings

# Web (from web/)
npm install && npm run dev             # -> http://localhost:3000

# Lint / format (Python)
ruff check . && ruff format .
```

## Environment

Copy `.env.example` to `.env` and fill in keys. The user has access to:
Anthropic, OpenAI, a web-search API (Tavily/SerpAPI), GitHub token, Kaggle
token+username. Local models via Ollama are the zero-cost fallback. **Never**
commit `.env` or real secrets; `.gitignore` excludes them.

## Conventions

- Python: type hints everywhere, `ruff` for lint+format, `pydantic` for I/O
  schemas, snake_case modules.
- Each ingestion source is a thin adapter subclassing the base in
  [`ingestion/sources/base.py`](ingestion/sources/base.py) and registered in
  [`ingestion/registry.yaml`](ingestion/registry.yaml). Adapters must be
  schema-tolerant (never assume a field exists) and emit the canonical
  `NormalizedListing`.
- New work should be tagged with `TODO(phase-N)` so the roadmap stays legible.
- Tests live next to the service (`backend/tests/`) and in top-level `tests/`
  for cross-service flows.

## Where to start reading code

`backend/app/main.py` -> `backend/app/api/` (routers) -> `backend/app/models/`
(schema) -> `agents/graphs/` (orchestration) -> `ingestion/sources/base.py`
(adapter contract) -> `ranking/scorer.py` (score blend + explanation).
