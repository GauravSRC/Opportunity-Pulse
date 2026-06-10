"""Discovery graph: select_sources -> fan-out adapters -> fetch -> parse ->
emit_raw -> normalize.

Per-adapter retry+backoff; one adapter failing isolates and updates source
health; caching via ETag/fingerprint. See docs/agents.md#2-discovery.

TODO(phase-1): build the StateGraph over agents.state.DiscoveryState with
nodes calling the ingestion adapters and ingestion.normalize.
"""

from __future__ import annotations

from agents.state import DiscoveryState


def build_discovery_graph():
    """Return a compiled LangGraph for discovery. TODO(phase-1)."""
    raise NotImplementedError("build_discovery_graph")


# Node stubs ----------------------------------------------------------------
def select_sources(state: DiscoveryState) -> DiscoveryState: ...  # TODO(phase-1)
def fetch(state: DiscoveryState) -> DiscoveryState: ...  # TODO(phase-1)
def parse(state: DiscoveryState) -> DiscoveryState: ...  # TODO(phase-1)
def normalize(state: DiscoveryState) -> DiscoveryState: ...  # TODO(phase-1)
