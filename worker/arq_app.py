"""Arq worker settings and job registration.

Run: ``arq worker.arq_app.WorkerSettings``.

Cron jobs trigger discovery on a schedule; on-demand jobs (dedup+rank, outreach,
deadline, alerts) are enqueued by the API. Each job delegates to a LangGraph in
``agents.graphs`` and is idempotent (keyed by content fingerprint where
relevant). See docs/architecture.md (worker section).
"""

from __future__ import annotations

from worker.tasks import alerts, deadline, decay, dedup, ingest, normalize, rank

# Functions exposed to Arq. TODO(phase-1+): flesh out each task body.
FUNCTIONS = [
    ingest.run_discovery,
    normalize.run_normalize,
    dedup.run_dedup,
    rank.run_ranking,
    deadline.run_deadline,
    decay.run_decay,
    alerts.run_alerts,
]


async def startup(ctx: dict) -> None:
    # TODO(phase-1): open DB engine / Redis / warm embedding model into ctx.
    pass


async def shutdown(ctx: dict) -> None:
    # TODO(phase-1): dispose resources opened in startup.
    pass


class WorkerSettings:
    """Arq entrypoint configuration."""

    functions = FUNCTIONS
    on_startup = startup
    on_shutdown = shutdown
    # cron_jobs configured in Phase 1, e.g. discovery every 30 min.
    # redis_settings is read from REDIS_URL via RedisSettings.from_dsn at runtime.
