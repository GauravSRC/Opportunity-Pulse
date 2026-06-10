"""Admin monitoring endpoints.

TODO(phase-6/7): aggregate pipeline status, source health, and the latest eval
snapshot for the admin dashboard.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def admin_health() -> dict:
    # Placeholder shape; later aggregates real metrics.
    return {
        "pipeline": {"status": "unknown"},
        "sources": {"enabled": 0, "disabled": 0, "flapping": 0},
        "eval": {"last_run": None},
    }
