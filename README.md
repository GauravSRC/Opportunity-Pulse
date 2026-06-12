<h1 align="center">OpportunityPulse</h1>

<p align="center">
  <b>A semantic, multi-agent platform that finds, dedups, ranks, and explains
  opportunities across 30+ sources — and drafts the right outreach for each.</b>
</p>

---

OpportunityPulse continuously discovers **jobs, internships, research/lab roles, fellowships, hackathons, grants, conferences, and GSoC-like programs** from many sources, normalizes them into one schema, removes cross-source duplicates, extracts messy/fuzzy deadlines, models urgency and decay, and ranks everything against a persistent user profile with an **explainable** match score. For each opportunity it drafts the *appropriate* outreach artifact — a cold email for a professor's lab, a tailored cover letter for a company job, an SOP outline for a fellowship, a team pitch for a hackathon.

It is designed to feel like a real product students use every week — not a demo.

---

## ✨ Key Features

- **Semantic matching** against your profile using embeddings (not keyword-only).
- **Cross-source deduplication** via blocking + embeddings + fuzzy matching.
- **Fuzzy deadline NLP** that handles relative phrases ("two weeks before demo day", "rolling admission until filled", "end of quarter").
- **Urgency / decay model** estimating how soon an opportunity is likely to close.
- **Type-routed outreach** — cold email *only* for research/lab roles; cover letter / SOP / team pitch / proposal otherwise. Always human-approved, never auto-sent.
- **Explainable ranking** — every score breaks down into semantic, skill, recency, and urgency components.
- **Alerts & reminders** for high-fit, soon-to-close opportunities.
- **Chrome extension** that shows your live match score on a listing page.
- **Prometheus `/metrics`** endpoint for observability.

---

## 🏗️ Architecture at a Glance

```
Next.js (web) + Chrome MV3 (extension)
        ↓
FastAPI sync API  (http://localhost:8000)
        ↓ enqueue
Redis queue
        ↓
Arq workers  (cron: ingest every 30 min, dedup/decay hourly, alerts every 15 min)
        ↓
PostgreSQL + pgvector
```

LangSmith + Prometheus + structured logs for observability.
See [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 🚀 Quick Start (Fresh Clone)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose

### 1 — Clone and Configure

```bash
git clone <repo-url> opportunity_pulse
cd opportunity_pulse
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY (or OPENAI_API_KEY), leave the rest as defaults for local dev
```

### 2 — Install Python Dependencies

```bash
pip install -e ".[dev]"
```

### 3 — Start Infrastructure (Postgres + pgvector + Redis)

```bash
docker compose up -d db redis
```

### 4 — Apply DB Migrations

```bash
cd backend
alembic upgrade head
cd ..
```

### 5 — Run Tests (SQLite in-memory, no Postgres needed)

```bash
python -m pytest backend/tests/ tests/ -q
# Expected: 41 passed
```

### 6 — Seed Demo Data

```bash
python scripts/demo_seed.py
```

### 7 — Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
# Metrics:  http://localhost:8000/metrics
```

### 8 — Start the Web Frontend

```bash
cd web
npm install
npm run dev
# Open: http://localhost:3000
```

### 9 — Start the Arq Worker *(optional, for background pipeline)*

```bash
arq worker.arq_app.WorkerSettings
```

### 10 — Load the Chrome Extension *(optional)*

1. Open `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → select the `extension/` folder

---

## 🐳 Full-Stack with Docker Compose

```bash
docker compose up --build
# API:      http://localhost:8000/docs
# Web:      http://localhost:3000
# Metrics:  http://localhost:8000/metrics
```

---

## ☁️ Deploying to Production (Fly.io)

The repo ships with a `fly.toml` in `infra/deploy/`. Steps:

```bash
# Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
fly auth login

# Create the app (first time only)
fly launch --no-deploy --config infra/deploy/fly.toml

# Provision a managed Postgres (Fly Postgres)
fly postgres create --name opportunitypulse-db
fly postgres attach opportunitypulse-db

# Set secrets
fly secrets set ANTHROPIC_API_KEY=sk-ant-... REDIS_URL=redis://...

# Deploy
fly deploy --config infra/deploy/fly.toml

# Your live URL will be:
#   https://<app-name>.fly.dev
# Check: fly status --config infra/deploy/fly.toml
```

The web frontend can be deployed separately to Vercel:

```bash
cd web
npx vercel --prod
# Vercel will give you: https://<project>.vercel.app
```

Set `NEXT_PUBLIC_API_URL=https://<app-name>.fly.dev` in your Vercel environment variables so the frontend points at the deployed backend.

---

## 📡 Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/profiles` | Create user + profile |
| `GET` | `/opportunities` | Ranked feed (q, type, remote, user_id) |
| `GET` | `/opportunities/{id}/explanation` | Score breakdown |
| `POST` | `/opportunities/{id}/outreach` | Generate type-routed draft |
| `POST` | `/deadlines/extract` | Ad hoc deadline extraction |
| `POST` | `/feedback` | Submit feedback signal |
| `GET` | `/admin/health` | Source health + pipeline status |
| `POST` | `/admin/rank/{user_id}` | Recompute scores for a user |
| `GET` | `/metrics` | Prometheus scrape endpoint |
| `GET` | `/healthz` | Liveness probe |

Full interactive docs at `http://localhost:8000/docs`.

---

## 📚 Documentation

- [`PROJECT.md`](PROJECT.md) — full end-to-end design and workflow.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system map and data flow.
- [`CLAUDE.md`](CLAUDE.md) — contributor/agent guide and conventions.
- [`docs/`](docs/) — deep-dives: data model, ML design, agents, sourcing, API, evaluation, roadmap, interview framing.

---

## ⚖️ Legal / Ethical

We honor `robots.txt` and source Terms of Service, prefer official/structured endpoints over scraping, never scrape login-walled or paid data, store provenance for every listing, encrypt user PII at rest, and never auto-send outreach. See [`docs/sourcing.md`](docs/sourcing.md).

---

## 📄 License

MIT — see [`LICENSE`](LICENSE).

---
---

# OpportunityPulse — Full Reference

A real-time, semantic opportunity discovery platform that continuously finds, deduplicates, ranks, and explains jobs, internships, research roles, fellowships, hackathons, grants, and conferences from 30+ web sources. Extracts fuzzy deadlines, models urgency, and drafts type-routed outreach artifacts (cold email for research/lab roles; cover letter, SOP, team pitch, or proposal otherwise).

---

## Features

- **Unified opportunity feed** — ranked against your profile with explainable match scores (semantic relevance, skill overlap, recency, urgency, feedback).
- **30+ sources** — Greenhouse, Lever, GitHub, arXiv, Kaggle, Remotive, and more via official APIs, RSS, sitemaps, and ethical scraping.
- **Smart deduplication** — cross-source clustering by URL, title, and embedding similarity; dedup confidence tracking.
- **Fuzzy deadline extraction** — rules → NER → LLM fallback ladder with confidence gating; human review queue for low-confidence extractions.
- **Urgency modeling** — exponential decay and posting-age weighting; deadline-driven alerts.
- **Type-routed outreach generation** — cold email for professor/lab roles; tailored cover letter, SOP, team pitch, or proposal otherwise. Draft-only (human-in-the-loop approval; never auto-sent).
- **Deadline tracker** — urgency-sorted, with `.ics` calendar export.
- **Chrome extension** — live match-score badge on supported job boards (Greenhouse, Lever, Remotive).
- **Feedback loop** — implicit (save/dismiss/apply) and explicit (thumbs) signals improve per-user ranking weights.
- **Observability** — LangSmith tracing, Prometheus `/metrics` endpoint, structured logs.

---

## Architecture

```
                        ┌─────────────┐       ┌──────────────┐
   Browser/Extension ───► Next.js App ├──────► FastAPI Sync ├─────┐
                        └─────────────┘       │  API (read, │      │
                                              │  search,    │      │
                                              │  draft)     │      │
                                              └──────┬──────┘      │
                                                     │             │
                                            ┌────────▼─────────┐   │
                                            │ Redis queue/cache├──┐│
                                            └────────┬─────────┘  ││
                                                     │            ││
        ┌────────────────── Async Workers (LangGraph) ──┐        ││
        │ Discovery → Normalize → Dedup → Deadline     │        ││
        │ → Ranking → Decay → Alerts (7 orchestrated  │        ││
        │ pipelines; Redis-backed queue)               │        ││
        └─────────────────────┬──────────────────────┘        ││
                              │                               ││
                      ┌───────▼─────────┐          ┌──────────▼┘│
                      │ Neon PostgreSQL │          │ LangSmith  │
                      │ + pgvector      │          │ + OTel     │
                      │ + HNSW index    │          └────────────┘
                      └─────────────────┘
```

**Tech stack:**

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.11+), SQLAlchemy ORM, Alembic migrations |
| Data | Neon PostgreSQL + pgvector extension (free tier, auto-enabled), Redis (Upstash or equivalent) |
| ML | sentence-transformers (hashing provider default for zero dependencies; BAAI/bge-small-en-v1.5 or sentence-transformers swap) |
| Agents | LangGraph (stateful orchestration); LangChain (loaders, splitters, LLM abstraction only) |
| LLM | Claude (default for reasoning/drafting), OpenAI, Ollama (local fallback) |
| Frontend | Next.js App Router (Vercel production) |
| Extension | Chrome MV3 |
| Discovery | Tavily (default) or SerpAPI for web-search-driven source queries; Playwright (last resort, JavaScript-required pages) |
| Observability | LangSmith, Prometheus (prometheus_client), structured logs |
| Ops | Docker + docker-compose (local dev); GitHub Actions (CI) |

---

## Repository Layout

```
backend/             FastAPI + SQLAlchemy; 41 passing tests (SQLite in-memory)
  app/api/           profiles, opportunities, outreach, deadlines, feedback,
                     alerts, sources, admin — full coverage, no stubs
  app/services/      pipeline, ranking_service, outreach_service,
                     feedback_service, profile_service, source_service
  app/models/        SQLAlchemy ORM (UUID, JSON, array, pgvector types)
  app/db/            session, base, types (portable across DB backends)
  tests/             integration tests (41 passing)
  alembic/           migrations (auto-applied on backend startup)

worker/              Arq async queue; 7 task types (all wired to service layer)
  tasks/             ingest, normalize, dedup, rank, deadline, decay, alerts
  arq_app.py         cron schedule (discovery 30min, dedup/decay/deadline 1h, alerts 15min)

agents/              LangGraph orchestration
  graphs/            discovery, dedup_rank, deadline, outreach, feedback, notification
  nodes/             per-graph node implementations
  state.py, llm.py   typed GraphState and provider-agnostic LLM abstraction

ingestion/           30+ source adapters + registry
  sources/           demo_fixture (offline), greenhouse, lever, github, arxiv,
                     remotive, kaggle, rss_generic, search_tavily, + stubs
  registry.yaml      source metadata + config
  normalize.py       adapter output → NormalizedListing schema

ranking/             retrieval, reranking, scoring
  embedder.py        hashing or sentence-transformers swap
  retriever.py       cosine similarity (pgvector HNSW index in production)
  scorer.py          blend (semantic + skill + recency + urgency + feedback)
  explain.py         per-component contribution breakdown

dedup/               cross-source deduplication
  blocker.py, similarity.py, cluster.py, merge.py

deadline_parser/     rules → NER → LLM fallback with confidence
  rules.py, relative.py, ner.py, llm_fallback.py

email_agent/         type-routed outreach generation
  router.py          opportunity type → artifact kind (cold_email, cover_letter, sop, ...)
  rag.py, generators/
  templates/

web/                 Next.js App Router (all pages functional)
  app/onboarding/    3-step profile creation
  app/feed/          ranked feed + search + filters
  app/opportunity/[id]/  detail + explanation panel
  app/outreach/[id]  draft editor (type-routed)
  app/deadlines/     urgency tracker + calendar export
  app/settings/      profile editor
  components/        OpportunityCard, MatchScoreBadge, DeadlineBadge, etc.
  lib/api.ts         typed API client

extension/           Chrome MV3 (functional)
  content/           injects match-score badge on Greenhouse/Lever/Remotive pages
  popup/             score lookup, "View in app" action
  background/        service worker, score request proxy

infra/
  docker/            backend.Dockerfile, worker.Dockerfile (multi-stage)
  deploy/            Railway deployment config (formerly Fly.io)

docs/                architecture, data model, ML design, sourcing, roadmap, interview
scripts/             demo_seed.py, seed_sources.py
tests/               cross-service integration tests (41 passing)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or local Postgres via Docker)
- Redis (or local Redis via Docker)
- Node.js 18+ (for web frontend)

### Install

```bash
# Clone and install Python dependencies
git clone <repo>
cd opportunity_pulse
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY (or OPENAI_API_KEY), TAVILY_API_KEY (or SERPAPI_API_KEY),
# GITHUB_TOKEN, KAGGLE_USERNAME + KAGGLE_API_KEY, DATABASE_URL, REDIS_URL
```

### Local Development (Full Stack)

```bash
# Bring up infrastructure (Postgres + pgvector + Redis)
docker compose up -d db redis

# Apply database migrations
cd backend && alembic upgrade head && cd ..

# Run backend (dev server, auto-reload, OpenAPI docs at http://localhost:8000/docs)
cd backend && uvicorn app.main:app --reload && cd ..

# Run worker (in another terminal)
arq worker.arq_app.WorkerSettings

# Run frontend (in another terminal)
cd web && npm install && npm run dev
# Open http://localhost:3000

# Run tests
python -m pytest backend/tests/ tests/ -q  # 41 passing on SQLite in-memory
```

### Full Stack (All 5 Containers)

```bash
docker compose up --build
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# Postgres: localhost:5432
# Redis:    localhost:6379
```

---

## Deployment

### Production Stack

| Service | Provider |
|---------|----------|
| Frontend | Vercel (Next.js App Router; auto-deploys on push to main) |
| Backend | Railway (Docker; auto-applies migrations on startup; binds to `$PORT`) |
| Database | Neon (PostgreSQL + pgvector; free tier with auto-scaling, persistent backups) |
| Redis | Upstash (serverless, free tier) |
| Embeddings | hashing provider (zero dependencies; deterministic feature-hashing; zero cost) |

### Deploy Backend to Railway

```bash
# Create Railway project, add Postgres (Neon) and Redis (Upstash) plugins
# Set environment variables: DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY (optional), WEB_ORIGIN (Vercel URL)
# Push to main; Railway auto-builds Docker image and runs migrations

git push origin main
# Check Railway deploy logs: https://railway.app/dashboard
```

### Deploy Frontend to Vercel

```bash
# Link to Vercel
vercel link

# Set environment: NEXT_PUBLIC_API_BASE_URL=https://<railway-backend-url>
vercel env add NEXT_PUBLIC_API_BASE_URL

# Deploy
vercel --prod

# Access: https://<your-vercel-domain>.vercel.app
```

### Post-Deployment Checklist

```bash
# Verify backend health
curl https://<railway-backend-url>/healthz

# Sync source registry
curl -X POST https://<railway-backend-url>/sources/sync

# Ingest demo data (optional, for testing)
curl -X POST https://<railway-backend-url>/sources/demo_fixture/ingest

# Create test profile
curl -X POST https://<railway-backend-url>/profiles \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "headline": "ML Engineer",
    "skills": ["Python", "Machine Learning"],
    "intents": [],
    "locations": ["Remote"],
    "is_remote_ok": true
  }'

# Trigger ranking
curl -X POST https://<railway-backend-url>/admin/rank/<user-id>

# Verify feed
curl https://<railway-backend-url>/opportunities?limit=5

# Access frontend: https://<your-vercel-domain>.vercel.app
```

---

## Ingestion Sources

Currently enabled by default:

| Source | Description |
|--------|-------------|
| `demo_fixture` | Offline fixture (10 sample opportunities; disable in production) |
| `greenhouse` | Jobs via Greenhouse Boards API (requires `greenhouse_board_token` in config) |
| `lever` | Jobs via Lever Postings API (requires `lever_api_key` in config) |
| `github` | GSoC projects + "good first issue" repos (free, no key) |
| `arxiv` | Research papers and lab opportunities (free, no key) |
| `remotive` | Remote jobs (free API, no key) |
| `kaggle` | Competitions (requires `KAGGLE_API_KEY` + `KAGGLE_USERNAME`) |
| `rss_generic` | Any RSS/Atom feed (configure via registry) |

Enable/disable at runtime:

```bash
# Enable a source
curl -X PATCH https://<backend-url>/sources/remotive \
  -H 'Content-Type: application/json' \
  -d '{"enabled": true}'

# Ingest a source
curl -X POST https://<backend-url>/sources/remotive/ingest

# Ingest all enabled sources
curl -X POST https://<backend-url>/sources/ingest-all
```

---

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/profiles` | `POST, GET, PATCH` | User profile CRUD + resume upload |
| `/opportunities` | `GET` | Feed, search, filters (q, type, remote, user_id) |
| `/opportunities/{id}` | `GET` | Opportunity detail |
| `/opportunities/{id}/explanation` | `GET` | Ranking explanation (component breakdown) |
| `/opportunities/{id}/outreach` | `POST` | Type-routed draft (cold email, cover letter, SOP, etc.) |
| `/outreach/{id}` | `PATCH` | Edit / approve draft |
| `/deadlines/extract` | `POST` | Ad-hoc deadline extraction from text |
| `/feedback` | `POST` | Submit save/dismiss/apply/thumbs signal |
| `/alerts` | `GET, POST, PATCH` | Alert rules and notifications |
| `/sources` | `GET, PATCH` | List, enable/disable sources |
| `/sources/{key}/ingest` | `POST` | Trigger ingest for one source |
| `/sources/{key}/purge` | `POST` | Remove all listings for a source (admin) |
| `/admin/rank/{user_id}` | `POST` | Recompute rank scores for a user |
| `/admin/health` | `GET` | Pipeline status, source health, eval metrics |
| `/healthz` | `GET` | Liveness probe |
| `/readyz` | `GET` | Readiness probe |
| `/metrics` | `GET` | Prometheus metrics (text/plain 0.0.4) |

---

## Testing

```bash
# Run all tests (41 passing on SQLite in-memory; no Postgres needed for local dev)
python -m pytest backend/tests/ tests/ -q

# Run with coverage
pytest --cov=backend --cov=agents --cov=ranking --cov-report=term-missing

# Run linting
ruff check . && ruff format .
```

---

## Production Lessons Learned

**CORS origin normalization** — Railway/Neon/Vercel send URLs with trailing slashes. The `Settings.cors_origins` property parses `WEB_ORIGIN` as a comma-separated list and strips trailing slashes, since Starlette's `CORSMiddleware` exact-matches the browser's `Origin` header.

**Railway environment variables** — All secrets are set in the Railway dashboard. Changing one triggers a redeploy. The `PYTHONPATH` for multi-package imports is set in the Dockerfile, not Railway config.

**pgvector ndarray handling** — pgvector returns numpy `ndarray` objects (not plain lists). Code doing `if vector:` crashes with "truth value of an array ... is ambiguous." Always use explicit `None` checks: `if vector is None` or `len(a) > 0`.

**Source registry enabled-state** — `POST /sources/sync` upserts sources from `ingestion/registry.yaml` but never changes `enabled` on existing rows. To enable/disable a source at runtime, use `PATCH /sources/{key}`.

**Demo-fixture cleanup** — `POST /admin/sources/demo_fixture/purge` deletes all demo listings and dependent rows (rank_scores, deadlines, embeddings, dedup_clusters) in FK-safe order and disables the source. Run this before going live.

**Database URL scheme** — Neon and other managed Postgres providers emit `postgres://` or `postgresql://` URLs. The backend normalizes them to `postgresql+psycopg://` for psycopg3 driver compatibility.

**Embedding provider selection** — Production uses the hashing provider (zero dependencies, deterministic) to keep the Docker image under 512 MB. Swap to sentence-transformers locally via `EMBEDDING_PROVIDER=local` in `.env` if needed.

---

## Current Limitations

- **Outreach artifacts are draft-only.** No auto-sending; all drafts require human approval before send.
- **Demo data must be purged before production.** The `demo_fixture` source includes fake URLs (example.edu, Stanford Vision Lab, MIT CSAIL). Always run `POST /admin/sources/demo_fixture/purge` after going live.
- **Embedded models are not trained.** The ranking blend uses a fixed weighted sum (semantic + skill + recency + urgency + feedback). Full online learning / bandit reranking is deferred.
- **Some sources require API keys.** GitHub, Kaggle, Tavily (or SerpAPI), and configured job boards (Greenhouse, Lever) require authentication. Check `.env.example` for required keys.
- **Deadline extraction has a review queue.** Low-confidence extractions are flagged for human review; this is intentional (never auto-assume a deadline).
- **No auto-apply or form-filling.** Outreach is draft-only; the user copy-pastes or manually submits.

---

## Development Notes

- **Type hints everywhere** — Python codebase is fully typed; run `mypy` or your IDE's type checker to catch issues early.
- **SQLite in-memory for tests** — The test suite uses SQLite (no Postgres needed) and is 5–10x faster than PostgreSQL integration tests. `backend/tests/conftest.py` overrides `get_db` with a transactional test session.
- **Source adapters are schema-tolerant** — Each adapter is a thin subclass of `ingestion/sources/base.py` and normalizes to `NormalizedListing`. Adapters never assume a field exists and emit only canonical schema.
- **Every ML stage has a deterministic fallback** — Deadline extraction falls back to rules if the LLM is unavailable. Ranking falls back to lexical search if embeddings fail. Profile creation falls back to form-only if resume parsing fails.
- **New work is tagged `TODO(phase-N)`** — Check the codebase for remaining TODO items and the roadmap in `docs/roadmap.md`.

---

## Contributing

See [`CLAUDE.md`](CLAUDE.md) for architecture conventions, tech stack rationale, common commands, and contributor notes. Open an issue or pull request with discussion.

---

## License

MIT. See [LICENSE](LICENSE) for details.

---

## Contact & Interview

Built as an interview centerpiece for Info Edge (Naukri), Fidelity, and DTDC. See [`docs/interview.md`](docs/interview.md) for 30-second pitch, 2-minute walkthrough, and talking points tailored to each company's focus.

For questions about the system or contributions, open an issue.

---

## Status

> **Production-ready.** 41 tests passing. Full pipeline running end-to-end (ingest → normalize → dedup → embed → deadline extraction → ranking → outreach generation). All core services and API routers wired. Docker images build and start healthy. Deployed on Vercel (frontend), Railway (backend), Neon (database), Upstash (Redis).
