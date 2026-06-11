# Deploying OpportunityPulse — Render (backend) + Vercel (frontend)

This is the production deployment path used in place of Fly.io. The backend ships
as a Docker image on **Render**; the Next.js frontend deploys on **Vercel**;
Postgres is **Neon** (persistent free tier, pgvector) and Redis is **Upstash**
(free tier).

> All of these have a free tier except the Arq **worker** (Render background
> workers are paid). The worker is optional — without it the API is fully
> functional and you trigger ingestion/ranking via the API endpoints.

## Why Docker (not native Python) on Render

The repo is a monorepo where importable packages live in two roots — top-level
(`ranking`, `dedup`, `ingestion`, …) under `/app` and the FastAPI `app` package
under `/app/backend` — wired via `PYTHONPATH=/app:/app/backend` and a hatchling
`sources` remap. The existing Dockerfiles already solve this exactly. A native
Render Python buildpack would have to re-derive the `PYTHONPATH` and the
multi-package layout by hand and would drift from the tested local build. Docker
reuses the artifact that already runs healthy locally. **Use Docker.**

## Environment variables

### Backend (Render web service)

| Variable | Required | Value |
|---|---|---|
| `DATABASE_URL` | ✅ | Neon/Render Postgres URL. `postgres://`/`postgresql://` is auto-normalized to the psycopg3 driver. Append `?sslmode=require` for Neon. |
| `REDIS_URL` | ✅ (worker) | Upstash `rediss://...` URL. API boots without it; the worker needs it. |
| `WEB_ORIGIN` | ✅ | Frontend origin for CORS, e.g. `https://opportunity-pulse.vercel.app` (no trailing slash). |
| `APP_ENV` | ✅ | `production` |
| `APP_SECRET` | ✅ | Random string (Render `generateValue` does this). |
| `EMBEDDING_PROVIDER` | recommended | `hashing` — zero deps, fits the free 512 MB runtime. |
| `RERANK_ENABLED` | recommended | `false` on free tier. |
| `LLM_PROVIDER` + `ANTHROPIC_API_KEY` | optional | Enables outreach/deadline LLM; degrades gracefully if unset. |
| `PROMETHEUS_ENABLED` | optional | `true` |

### Frontend (Vercel)

| Variable | Required | Value |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | ✅ | `https://opportunity-pulse-api.onrender.com` (your Render API URL, no trailing slash). |

### Worker (Render background worker, optional/paid)

Same as backend minus the web-only vars: `DATABASE_URL`, `REDIS_URL`, `APP_ENV`,
`EMBEDDING_PROVIDER`, `LLM_PROVIDER`, `ANTHROPIC_API_KEY`.

## Data store choices

**Postgres — recommended: Neon.** Free tier is persistent (Render's free Postgres
is deleted after 30 days), serverless, and supports the `vector` (pgvector) and
`uuid-ossp` extensions the initial migration creates. Render Postgres works too if
you prefer one dashboard. Supabase/Railway also work (all expose a standard
Postgres URL the app normalizes). The migration runs `CREATE EXTENSION IF NOT
EXISTS vector` so pgvector support is the only hard compatibility requirement.

**Redis — recommended: Upstash.** Free tier, TLS `rediss://` URL that redis-py/Arq
accept directly. Render Key Value or Redis Cloud also work. Arq only needs a
reachable Redis; no special config.

## Migrations

The backend image's production command runs `alembic upgrade head` before starting
uvicorn (see `infra/docker/backend.Dockerfile`). Migrations apply automatically on
every backend deploy/boot — idempotent, so re-running is a no-op. The worker does
not run migrations; deploy the backend first so the schema exists.

---

## Copy-paste deployment guide

### 0. Prerequisites
- GitHub repo pushed: https://github.com/GauravSRC/Opportunity-Pulse
- Accounts: Render, Vercel, Neon, Upstash (all free to sign up).

### 1. Postgres on Neon
1. https://neon.tech → New Project → name `opportunitypulse`.
2. Copy the connection string (looks like `postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require`).
3. Keep it — this is your `DATABASE_URL`. (No need to manually enable pgvector; the
   migration does `CREATE EXTENSION IF NOT EXISTS vector`. Neon allows it.)

### 2. Redis on Upstash
1. https://upstash.com → Create Database → Redis → pick a region near your Render region.
2. Copy the **`rediss://`** URL from the "Redis" connect tab → this is your `REDIS_URL`.

### 3. Backend on Render (via Blueprint)
1. https://dashboard.render.com → **New** → **Blueprint**.
2. Connect the GitHub repo. Render reads `render.yaml`.
3. If you want a FREE-only deploy, delete the `opportunity-pulse-worker` service
   from `render.yaml` first (background workers are paid), commit, and re-sync.
4. Render prompts for the `sync: false` vars on the `opportunity-pulse-api` service:
   - `DATABASE_URL` = Neon URL (from step 1)
   - `REDIS_URL` = Upstash URL (from step 2)
   - `WEB_ORIGIN` = leave as a placeholder for now (you'll set it in step 5 once you
     know the Vercel URL); e.g. `https://opportunity-pulse.vercel.app`
   - `ANTHROPIC_API_KEY` = your key (optional)
5. Click **Apply**. First build takes several minutes (Docker image). When live,
   note the URL, e.g. `https://opportunity-pulse-api.onrender.com`.
6. Verify: open `https://<api>.onrender.com/healthz` → `{"status":"ok"}`, and
   `https://<api>.onrender.com/docs` for the API explorer.

### 4. Frontend on Vercel
1. https://vercel.com → **Add New** → **Project** → import the GitHub repo.
2. **Root Directory: `web`** (important — the Next.js app is in `web/`).
3. Framework preset auto-detects **Next.js**. Leave build/output defaults.
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_BASE_URL` = your Render API URL from step 3 (no trailing slash).
5. **Deploy**. Note the URL, e.g. `https://opportunity-pulse.vercel.app`.

### 5. Wire CORS (back to Render)
1. In Render → `opportunity-pulse-api` → Environment → set `WEB_ORIGIN` to the exact
   Vercel URL from step 4 → Save (triggers a redeploy).

### 6. Worker (optional, paid)
If you kept the worker service in `render.yaml`, set its `DATABASE_URL`, `REDIS_URL`,
and `ANTHROPIC_API_KEY` the same as the backend. It starts polling Redis and runs the
cron schedule (discovery, dedup, decay, deadline, alerts). On free tier (no worker),
trigger the same work manually via the API (see checklist below).

### 7. Seed demo data (optional)
With the backend live, from your machine:
```bash
export NEXT_PUBLIC_API_BASE_URL=  # not needed for the script
DATABASE_URL="<your-neon-url>" python scripts/demo_seed.py
```
Or use the API: `POST /sources/sync` → `POST /sources/ingest-all` → `POST /admin/rank/{user_id}`.

---

## Deployment order
1. Neon Postgres → get `DATABASE_URL`
2. Upstash Redis → get `REDIS_URL`
3. Render backend (Blueprint) → runs migrations on boot → get API URL
4. Vercel frontend → set `NEXT_PUBLIC_API_BASE_URL` → get web URL
5. Render backend → set `WEB_ORIGIN` to the Vercel URL (CORS)
6. (optional) Render worker → set DB/Redis/LLM vars
7. (optional) seed demo data

## Expected public URLs
- Backend: `https://opportunity-pulse-api.onrender.com`
- Frontend: `https://opportunity-pulse.vercel.app`

## Post-deployment testing checklist
- [ ] `GET /healthz` → `{"status":"ok"}`
- [ ] `GET /readyz` → `{"status":"ready"}`
- [ ] `GET /docs` loads the OpenAPI UI
- [ ] `GET /metrics` returns Prometheus text (200)
- [ ] Frontend loads; onboarding submits → `POST /profiles` succeeds (no CORS error in console)
- [ ] Feed page fetches `/opportunities` from the Render URL (Network tab shows the onrender.com host)
- [ ] Opportunity detail "Why it matched" panel loads `/opportunities/{id}/explanation`
- [ ] Outreach generation returns a type-routed artifact (cold email only for research/lab)
- [ ] If worker deployed: a discovery/rank cron cycle populates the feed; else trigger via API
- [ ] Browser console shows no `localhost:8000` requests (confirms `NEXT_PUBLIC_API_BASE_URL` took effect)
