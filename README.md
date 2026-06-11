<h1 align="center">OpportunityPulse</h1>

<p align="center">
  <b>A semantic, multi-agent platform that finds, dedups, ranks, and explains
  opportunities across 30+ sources — and drafts the right outreach for each.</b>
</p>

---

OpportunityPulse continuously discovers **jobs, internships, research/lab roles,
fellowships, hackathons, grants, conferences, and GSoC-like programs** from many
sources, normalizes them into one schema, removes cross-source duplicates,
extracts messy/fuzzy deadlines, models urgency and decay, and ranks everything
against a persistent user profile with an **explainable** match score. For each
opportunity it drafts the *appropriate* outreach artifact — a cold email for a
professor's lab, a tailored cover letter for a company job, an SOP outline for a
fellowship, a team pitch for a hackathon.

It is designed to feel like a real product students use every week — not a demo.

## Key features

- **Semantic matching** against your profile using embeddings (not keyword-only).
- **Cross-source deduplication** via blocking + embeddings + fuzzy matching.
- **Fuzzy deadline NLP** that handles relative phrases ("two weeks before demo
  day", "rolling admission until filled", "end of quarter").
- **Urgency / decay model** estimating how soon an opportunity is likely to close.
- **Type-routed outreach** — cold email *only* for research/lab roles; cover
  letter / SOP / team pitch / proposal otherwise. Always human-approved, never
  auto-sent.
- **Explainable ranking** — every score breaks down into semantic, skill,
  recency, and urgency components.
- **Alerts & reminders** for high-fit, soon-to-close opportunities.
- **Chrome extension** that shows your live match score on a listing page.
- **Prometheus `/metrics`** endpoint for observability.

## Architecture at a glance

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

## Quick start (fresh clone)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose

### 1 — Clone and configure

```bash
git clone <repo-url> opportunity_pulse
cd opportunity_pulse
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY (or OPENAI_API_KEY), leave the rest as defaults for local dev
```

### 2 — Install Python dependencies

```bash
pip install -e ".[dev]"
```

### 3 — Start infrastructure (Postgres + pgvector + Redis)

```bash
docker compose up -d db redis
```

### 4 — Apply DB migrations

```bash
cd backend
alembic upgrade head
cd ..
```

### 5 — Run tests (SQLite in-memory, no Postgres needed)

```bash
python -m pytest backend/tests/ tests/ -q
# Expected: 41 passed
```

### 6 — Seed demo data

```bash
python scripts/demo_seed.py
```

### 7 — Start the backend API

```bash
cd backend
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
# Metrics:  http://localhost:8000/metrics
```

### 8 — Start the web frontend

```bash
cd web
npm install
npm run dev
# Open: http://localhost:3000
```

### 9 — Start the Arq worker (optional, for background pipeline)

```bash
arq worker.arq_app.WorkerSettings
```

### 10 — Load the Chrome extension (optional)

1. Open `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → select the `extension/` folder

---

## Full-stack with Docker Compose

```bash
docker compose up --build
# API:      http://localhost:8000/docs
# Web:      http://localhost:3000
# Metrics:  http://localhost:8000/metrics
```

---

## Deploying to production (Fly.io)

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

Set `NEXT_PUBLIC_API_URL=https://<app-name>.fly.dev` in your Vercel environment
variables so the frontend points at the deployed backend.

---

## Key API endpoints

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

## Documentation

- [`PROJECT.md`](PROJECT.md) — full end-to-end design and workflow.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — system map and data flow.
- [`CLAUDE.md`](CLAUDE.md) — contributor/agent guide and conventions.
- [`docs/`](docs/) — deep-dives: data model, ML design, agents, sourcing, API,
  evaluation, roadmap, interview framing.

## Legal / ethical

We honor `robots.txt` and source Terms of Service, prefer official/structured
endpoints over scraping, never scrape login-walled or paid data, store
provenance for every listing, encrypt user PII at rest, and never auto-send
outreach. See [`docs/sourcing.md`](docs/sourcing.md).

## License

MIT — see [`LICENSE`](LICENSE).
