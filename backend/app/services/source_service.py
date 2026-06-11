"""Opportunity-source registry: sync YAML -> DB, list, and health updates."""

from __future__ import annotations

import pathlib

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import AccessMethod
from app.models.source import OpportunitySource

_REGISTRY = pathlib.Path(__file__).resolve().parents[3] / "ingestion" / "registry.yaml"


def sync_registry(db: Session, path: pathlib.Path | None = None) -> int:
    """Upsert sources from registry.yaml by key. Preserves runtime health/enabled
    state on existing rows except for config (refreshed)."""
    data = yaml.safe_load((path or _REGISTRY).read_text(encoding="utf-8"))
    sources = data.get("sources", [])
    for entry in sources:
        key = entry["key"]
        config = dict(entry.get("config") or {})
        config["_adapter"] = entry.get("adapter", key)
        row = db.execute(
            select(OpportunitySource).where(OpportunitySource.key == key)
        ).scalar_one_or_none()
        if row is None:
            row = OpportunitySource(
                key=key,
                name=entry.get("name", key),
                category=entry.get("category", "mixed"),
                access_method=AccessMethod(entry.get("access_method", "api")),
                base_url=entry.get("base_url"),
                config_json=config,
                enabled=bool(entry.get("enabled", True)),
                health_json={},
            )
            db.add(row)
        else:
            row.name = entry.get("name", row.name)
            row.category = entry.get("category", row.category)
            row.access_method = AccessMethod(entry.get("access_method", row.access_method.value))
            row.config_json = config
    db.commit()
    return len(sources)


def list_sources(db: Session) -> list[OpportunitySource]:
    return list(db.execute(select(OpportunitySource)).scalars())


def get_source(db: Session, key: str) -> OpportunitySource | None:
    return db.execute(
        select(OpportunitySource).where(OpportunitySource.key == key)
    ).scalar_one_or_none()
