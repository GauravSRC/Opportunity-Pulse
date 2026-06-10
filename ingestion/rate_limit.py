"""Per-host politeness: token-bucket rate limiting + backoff.

Used by every networked adapter. Backed by Redis so limits hold across worker
processes. See docs/sourcing.md (rate / anti-bot).
"""

from __future__ import annotations


class TokenBucket:
    """Per-host token bucket. TODO(phase-1): Redis-backed implementation."""

    def __init__(self, rate_per_sec: float, capacity: int | None = None) -> None:
        self.rate = rate_per_sec
        self.capacity = capacity or max(1, int(rate_per_sec * 5))

    async def acquire(self, host: str) -> None:
        raise NotImplementedError("TokenBucket.acquire")  # TODO(phase-1)


def backoff_seconds(attempt: int, base: float = 0.5, cap: float = 30.0) -> float:
    """Exponential backoff with jitter (deterministic helper)."""
    import random

    return min(cap, base * (2**attempt)) * (0.5 + random.random() / 2)
