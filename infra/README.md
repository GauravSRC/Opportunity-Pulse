# Infra

| Path | Purpose |
|---|---|
| `docker/backend.Dockerfile` | FastAPI image (build context = repo root) |
| `docker/worker.Dockerfile` | Arq worker image |
| `docker/web.Dockerfile` | Next.js image (build context = `./web`) |
| `deploy/fly.toml` | Fly.io deployment template (default cloud target) |
| `prometheus/prometheus.yml` | local Prometheus scrape config |

Local dev uses the root `docker-compose.yml` (pg+pgvector, redis, backend,
worker, web). Production builds the same images in CI and deploys via
`.github/workflows/deploy.yml`. Secrets are injected at deploy time — never
committed.
