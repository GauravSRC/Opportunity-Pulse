# Deploying OpportunityPulse — Railway (backend) + Neon (DB) + Vercel (frontend)

Production deployment path using Railway for the backend (and optional worker),
Neon for Postgres, and Vercel for the Next.js frontend. This replaces the
Render/Fly.io paths.

## 1. Railway readiness audit

| Concern | Status | Detail |
|---|---|---|
| Docker build | ✅ ready | `infra/docker/backend.Dockerfile` builds from repo-root context (`COPY backend ./backend`, etc.); Railway's Dockerfile build context is the repo root. |
| Dynamic port | ✅ ready | CMD binds `uvicorn ... --port ${PORT:-8000}`; Railway injects `PORT`. |
| DB driver | ✅ ready | `config.py` auto-rewrites Neon's `postgresql://` → `postgresql+psycopg://`. |
| Migrations | ✅ ready | Backend CMD runs `alembic upgrade head` before uvicorn (idempotent). |
| Health check | ✅ ready | `/healthz` returns 200; wired in `railway.json`. |
| Redis dependency | ✅ none on API | The FastAPI backend never connects to Redis — it's used **only** by the Arq worker. The API needs just `DATABASE_URL`. |
| Worker | ✅ ready | `worker.Dockerfile` CMD `arq worker.arq_app.WorkerSettings`; runs as an ordinary Railway service (no special tier). |
| CORS | ✅ env-driven | `WEB_ORIGIN` controls allowed origin; set to the Vercel URL. |
| Secrets | ✅ env-driven | All secrets come from env vars; nothing hardcoded. |

## 2. Code/config changes required for Railway

**No application code changes.** The work done for the Docker/Render path
(dynamic `$PORT`, DB-URL normalization, migration-on-start) makes the backend
Railway-compatible as-is. Two config files were added:

- `railway.json` (repo root) — backend service: Dockerfile builder + `/healthz`.
- `infra/railway/worker.json` — worker service config (point the worker service's
  "Config-as-code" path here).

## 3. Railway service configuration

You create **one Railway project** with two services from the same GitHub repo:

**Service A — `opportunity-pulse-api` (backend)**
- Source: the GitHub repo, root directory = repo root (default).
- Config: auto-detects root `railway.json` → Dockerfile build, `infra/docker/backend.Dockerfile`.
- Networking: Settings → Networking → **Generate Domain** (gives the public HTTPS URL).
- Start command: leave empty (the image CMD runs migrations + uvicorn).

**Service B — `opportunity-pulse-worker` (optional)**
- Source: same repo, root directory = repo root.
- Config: Settings → **Config-as-code** → set path to `infra/railway/worker.json`.
- Networking: none (no public domain; it only talks to Redis + Postgres).
- Needed only if you want automatic cron ingestion/ranking. Without it, trigger
  work via the API (`/sources/sync` → `/sources/ingest-all` → `/admin/rank/{id}`).

**Redis (only if you deploy the worker)**
- Railway → **New** → **Database** → **Redis** (one-click). Reference its URL in
  the worker as `${{Redis.REDIS_URL}}`. (Upstash also works — paste its `rediss://` URL.)

## 4. Required environment variables

### Backend service (`opportunity-pulse-api`)
| Variable | Required | Value |
|---|---|---|
| `DATABASE_URL` | ✅ | Neon URL (`postgresql://...neon.tech/neondb?sslmode=require`). Auto-normalized to psycopg3. |
| `WEB_ORIGIN` | ✅ | Vercel URL, e.g. `https://opportunity-pulse.vercel.app` (no trailing slash). |
| `APP_ENV` | ✅ | `production` |
| `APP_SECRET` | ✅ | A random string. |
| `EMBEDDING_PROVIDER` | recommended | `hashing` (zero deps; keeps runtime memory low). |
| `RERANK_ENABLED` | recommended | `false` |
| `PROMETHEUS_ENABLED` | optional | `true` |
| `LLM_PROVIDER` + `ANTHROPIC_API_KEY` | optional | Enables outreach/deadline LLM; degrades gracefully if unset. |

> The backend does **not** need `REDIS_URL`.

### Worker service (`opportunity-pulse-worker`, optional)
| Variable | Required | Value |
|---|---|---|
| `DATABASE_URL` | ✅ | Same Neon URL as the backend. |
| `REDIS_URL` | ✅ | `${{Redis.REDIS_URL}}` (Railway Redis) or an Upstash `rediss://` URL. |
| `APP_ENV` | ✅ | `production` |
| `EMBEDDING_PROVIDER` | recommended | `hashing` |
| `LLM_PROVIDER` + `ANTHROPIC_API_KEY` | optional | As above. |

### Frontend (Vercel)
| Variable | Required | Value |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | ✅ | Railway backend URL, e.g. `https://opportunity-pulse-api.up.railway.app` (no trailing slash). |

## 5. Neon setup
1. https://neon.tech → New Project → name `opportunitypulse`.
2. Copy the connection string (`postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`).
3. That string is `DATABASE_URL`. No manual extension setup — the migration runs
   `CREATE EXTENSION IF NOT EXISTS vector` (Neon supports pgvector).

## 6. Vercel setup
1. https://vercel.com → Add New → Project → import the GitHub repo.
2. **Root Directory = `web`** (critical — the Next.js app lives in `web/`).
3. Framework auto-detects **Next.js**; keep build defaults.
4. Environment Variable: `NEXT_PUBLIC_API_BASE_URL` = your Railway backend URL.
5. Deploy → note the URL (e.g. `https://opportunity-pulse.vercel.app`).

## 7. Deployment order
1. **Neon** → create project → get `DATABASE_URL`.
2. **Railway backend** → new project from repo → set `DATABASE_URL`, `APP_ENV`,
   `APP_SECRET`, `EMBEDDING_PROVIDER`, (optional `ANTHROPIC_API_KEY`) → Generate
   Domain. On boot it runs migrations and starts. Verify `/healthz`.
3. **Vercel** → import repo, root `web`, set `NEXT_PUBLIC_API_BASE_URL` to the
   Railway URL → deploy → get frontend URL.
4. **Railway backend** → set `WEB_ORIGIN` to the Vercel URL (CORS) → redeploys.
5. *(optional)* **Railway Redis** + **worker service** (config path
   `infra/railway/worker.json`) with `DATABASE_URL` + `REDIS_URL`.
6. *(optional)* Seed: `DATABASE_URL="<neon>" python scripts/demo_seed.py`, or use
   the API endpoints.

## 8. Post-deployment testing checklist
- [ ] `GET /healthz` → `{"status":"ok"}`
- [ ] `GET /readyz` → `{"status":"ready"}`
- [ ] `GET /docs` loads the OpenAPI UI
- [ ] `GET /metrics` returns Prometheus text (200)
- [ ] Frontend loads; onboarding submits (`POST /profiles`) with no CORS error
- [ ] Feed fetches `/opportunities` from the `*.up.railway.app` host (Network tab)
- [ ] "Why it matched" loads `/opportunities/{id}/explanation`
- [ ] Outreach returns a type-routed artifact (cold email only for research/lab)
- [ ] No `localhost:8000` requests in the browser console
- [ ] If worker deployed: a cron cycle populates the feed; else trigger via API

## 9. Expected public URLs
- Backend: `https://opportunity-pulse-api.up.railway.app`
- Frontend: `https://opportunity-pulse.vercel.app`

---

## Copy-paste deployment guide

```
0. Commit & push these config files (already in repo: railway.json,
   infra/railway/worker.json).

1. NEON
   neon.tech → New Project "opportunitypulse"
   → copy connection string → this is DATABASE_URL

2. RAILWAY (backend)
   railway.app → New Project → Deploy from GitHub repo → pick this repo
   Railway reads railway.json → builds infra/docker/backend.Dockerfile
   Variables (service → Variables):
     DATABASE_URL       = <Neon URL>
     APP_ENV            = production
     APP_SECRET         = <random string>
     EMBEDDING_PROVIDER = hashing
     RERANK_ENABLED     = false
     WEB_ORIGIN         = https://opportunity-pulse.vercel.app   (placeholder for now)
     ANTHROPIC_API_KEY  = <optional>
   Settings → Networking → Generate Domain
   → note URL, e.g. https://opportunity-pulse-api.up.railway.app
   Verify: open /healthz and /docs

3. VERCEL (frontend)
   vercel.com → Add New → Project → import repo
   Root Directory = web
   Env: NEXT_PUBLIC_API_BASE_URL = https://opportunity-pulse-api.up.railway.app
   Deploy → note URL, e.g. https://opportunity-pulse.vercel.app

4. RAILWAY (backend) → Variables → set WEB_ORIGIN = <exact Vercel URL> → redeploy

5. (optional) RAILWAY worker + Redis
   New → Database → Redis
   New → GitHub repo (same) → Settings → Config-as-code = infra/railway/worker.json
   Variables: DATABASE_URL = <Neon URL>, REDIS_URL = ${{Redis.REDIS_URL}},
              APP_ENV = production, EMBEDDING_PROVIDER = hashing

6. (optional) seed demo data:
   DATABASE_URL="<neon>" python scripts/demo_seed.py
```
