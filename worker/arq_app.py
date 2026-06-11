"""Arq worker settings and job registration.

Run: ``arq worker.arq_app.WorkerSettings`` from the repo root.

Cron jobs run discovery every 30 min, dedup+decay hourly, alerts every 15 min.
On-demand jobs (rank, deadline, normalize) are enqueued by the API layer.
"""

from __future__ import annotations

import os

from arq import cron
from arq.connections import RedisSettings

from worker.tasks import alerts, deadline, decay, dedup, ingest, normalize, rank

FUNCTIONS = [
    ingest.run_discovery,
    normalize.run_normalize,
    dedup.run_dedup,
    rank.run_ranking,
    deadline.run_deadline,
    decay.run_decay,
    alerts.run_alerts,
]

CRON_JOBS = [
    cron(ingest.run_discovery, minute={0, 30}),       # every 30 min
    cron(dedup.run_dedup, minute=5),                   # hourly at :05
    cron(decay.run_decay, minute=10),                  # hourly at :10
    cron(alerts.run_alerts, minute={0, 15, 30, 45}),  # every 15 min
    cron(deadline.run_deadline, minute=20),            # hourly at :20
]


async def startup(ctx: dict) -> None:
    pass


async def shutdown(ctx: dict) -> None:
    pass


def _redis_settings() -> RedisSettings:
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisSettings.from_dsn(url)


class WorkerSettings:
    """Arq entrypoint configuration."""

    functions = FUNCTIONS
    cron_jobs = CRON_JOBS
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = _redis_settings()
    max_jobs = 10
    job_timeout = 300
