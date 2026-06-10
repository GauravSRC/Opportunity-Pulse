"""Source-health monitoring.

Tracks success rate, parse-error rate, and freshness lag per source; auto-
disables a flapping source and raises an admin alert. Persisted to
opportunity_sources.health_json. See docs/sourcing.md (anti-brittleness).
"""

from __future__ import annotations

from dataclasses import dataclass

# A source dropping below this success rate over the window is auto-disabled.
MIN_SUCCESS_RATE = 0.5
MAX_PARSE_ERROR_RATE = 0.5


@dataclass
class SourceHealth:
    success_rate: float = 1.0
    parse_error_rate: float = 0.0
    freshness_lag_hours: float = 0.0
    consecutive_failures: int = 0

    @property
    def should_disable(self) -> bool:
        return (
            self.success_rate < MIN_SUCCESS_RATE
            or self.parse_error_rate > MAX_PARSE_ERROR_RATE
            or self.consecutive_failures >= 5
        )


def update_health(prev: dict, run_result: dict) -> SourceHealth:
    """Fold a run result into rolling health metrics. TODO(phase-1)."""
    raise NotImplementedError("update_health")
