"""Sync ingestion/registry.yaml into the opportunity_sources table.

Run after migrations to register/refresh sources. Idempotent (upsert by key).
TODO(phase-1): load YAML, upsert rows, preserve runtime health/enabled state.
"""

from __future__ import annotations

import pathlib

import yaml

REGISTRY = pathlib.Path(__file__).resolve().parents[1] / "ingestion" / "registry.yaml"


def load_registry() -> list[dict]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return data.get("sources", [])


def main() -> None:
    sources = load_registry()
    # TODO(phase-1): open a DB session and upsert each source by key.
    print(f"Loaded {len(sources)} sources from {REGISTRY.name} (upsert TODO phase-1).")


if __name__ == "__main__":
    main()
