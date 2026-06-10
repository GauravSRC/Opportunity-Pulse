"""Discovery/ingestion task — runs the discovery LangGraph for given sources."""

from __future__ import annotations


async def run_discovery(ctx: dict, source_keys: list[str] | None = None) -> dict:
    """Fetch + normalize listings for the given (or all enabled) sources.

    TODO(phase-1): build_discovery_graph().invoke(...) and persist raw +
    normalized listings; update source health.
    """
    raise NotImplementedError("run_discovery")
