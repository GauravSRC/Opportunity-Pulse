"""Opportunity-source registry: sync YAML -> DB, list, and health updates."""

from __future__ import annotations

import pathlib

import yaml
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models.deadline import Deadline
from app.models.embedding import Embedding
from app.models.enums import AccessMethod, EmbeddingOwner
from app.models.listing import DedupCluster, NormalizedListing, RawListing
from app.models.ranking import RankScore
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


def purge_source(db: Session, key: str, *, disable: bool = True) -> dict | None:
    """Delete all listings + dependent rows for one source. Returns counts.

    Removes seeded/demo data without touching other sources. Deletes in
    FK-dependency order: rank_scores -> deadlines -> embeddings -> dedup_clusters
    -> normalized_listings -> raw_listings. Returns ``None`` if the source key is
    unknown. When ``disable`` is set, the source is left disabled so a later
    ingest does not re-seed it.
    """
    source = get_source(db, key)
    if source is None:
        return None

    listing_ids = [
        row[0]
        for row in db.execute(
            select(NormalizedListing.id).where(NormalizedListing.source_id == source.id)
        ).all()
    ]

    deleted = {
        "rank_scores": 0,
        "deadlines": 0,
        "embeddings": 0,
        "clusters": 0,
        "listings": 0,
        "raw_listings": 0,
    }

    if listing_ids:
        deleted["rank_scores"] = db.execute(
            delete(RankScore).where(RankScore.listing_id.in_(listing_ids))
        ).rowcount
        deleted["deadlines"] = db.execute(
            delete(Deadline).where(Deadline.listing_id.in_(listing_ids))
        ).rowcount
        deleted["embeddings"] = db.execute(
            delete(Embedding).where(
                Embedding.owner_type == EmbeddingOwner.listing,
                Embedding.owner_id.in_(listing_ids),
            )
        ).rowcount
        # Drop clusters whose canonical listing is being removed; first detach any
        # listing still pointing at them so the cluster_id FK never dangles.
        cluster_ids = [
            row[0]
            for row in db.execute(
                select(DedupCluster.id).where(
                    DedupCluster.canonical_listing_id.in_(listing_ids)
                )
            ).all()
        ]
        if cluster_ids:
            db.execute(
                update(NormalizedListing)
                .where(NormalizedListing.cluster_id.in_(cluster_ids))
                .values(cluster_id=None)
            )
            deleted["clusters"] = db.execute(
                delete(DedupCluster).where(DedupCluster.id.in_(cluster_ids))
            ).rowcount

    deleted["listings"] = db.execute(
        delete(NormalizedListing).where(NormalizedListing.source_id == source.id)
    ).rowcount
    deleted["raw_listings"] = db.execute(
        delete(RawListing).where(RawListing.source_id == source.id)
    ).rowcount

    if disable:
        source.enabled = False
    db.commit()
    return {"source": key, "disabled": disable, "deleted": deleted}
