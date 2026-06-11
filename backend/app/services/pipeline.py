"""Ingestion + processing pipeline.

run_source: fetch -> parse -> persist raw + normalized -> embed -> extract
deadline (idempotent by source+external_id). dedup_all: cluster + merge across
all normalized listings. These are the plain-Python orchestration the worker and
demo_seed call; the LangGraph graphs in agents/graphs wrap the same steps.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.deadline import Deadline
from app.models.enums import DeadlineKind, EmbeddingOwner, Extractor, OpportunityType, RawStatus
from app.models.listing import DedupCluster, NormalizedListing, RawListing
from app.models.source import OpportunitySource
from app.services.embeddings import store_embedding
from dedup.blocker import candidate_pairs
from dedup.cluster import cluster as cluster_pairs
from dedup.merge import choose_canonical, merge_metadata
from dedup.similarity import is_duplicate, pair_score
from deadline_parser import extract as extract_deadline
from ingestion.sources import load_adapter
from ranking.embedder import embed_listing

log = get_logger(__name__)


def _fingerprint(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


async def run_source(db: Session, source: OpportunitySource, *, use_llm: bool = False) -> dict:
    """Fetch + process one source. Returns counts. Idempotent per external_id."""
    adapter_key = (source.config_json or {}).get("_adapter", source.key)
    adapter = load_adapter(adapter_key, source.config_json or {})

    created, skipped, errors = 0, 0, 0
    try:
        raw_records = await adapter.fetch()
    except Exception as exc:  # network/source failure isolates to this source
        log.warning("ingest.fetch_failed", source=source.key, error=str(exc))
        _record_health(source, ok=False)
        db.commit()
        return {"source": source.key, "created": 0, "skipped": 0, "errors": 1, "fetch_error": str(exc)}

    for rec in raw_records:
        try:
            exists = db.execute(
                select(NormalizedListing.id).where(
                    NormalizedListing.source_id == source.id,
                    NormalizedListing.url == rec.url,
                )
            ).first()
            if exists:
                skipped += 1
                continue

            raw = RawListing(
                source_id=source.id,
                external_id=str(rec.external_id),
                url=rec.url,
                fetched_at=rec.fetched_at or datetime.now(timezone.utc),
                payload_json=rec.payload,
                content_fingerprint=_fingerprint(rec.payload),
                status=RawStatus.new,
            )
            db.add(raw)
            db.flush()

            parsed = adapter.parse(rec)
            if parsed is None:
                raw.status = RawStatus.error
                errors += 1
                continue

            listing = NormalizedListing(
                raw_id=raw.id,
                source_id=source.id,
                title=parsed.title[:512],
                org=parsed.org,
                type=OpportunityType(parsed.type),
                location=parsed.location,
                is_remote=parsed.is_remote,
                url=parsed.url,
                posted_at=parsed.posted_at,
                description=parsed.description,
                skills=parsed.skills,
                links_json=parsed.links or {},
                is_canonical=True,
            )
            db.add(listing)
            db.flush()
            raw.status = RawStatus.normalized

            store_embedding(db, EmbeddingOwner.listing, listing.id, embed_listing(_listing_dict(listing)))
            _extract_and_store_deadline(db, listing, use_llm=use_llm)
            created += 1
        except Exception as exc:  # bad record never kills the run
            log.warning("ingest.parse_failed", source=source.key, error=str(exc))
            errors += 1

    source.last_run_at = datetime.now(timezone.utc)
    _record_health(source, ok=True, created=created, errors=errors)
    db.commit()
    return {"source": source.key, "created": created, "skipped": skipped, "errors": errors}


def _listing_dict(listing: NormalizedListing) -> dict:
    return {
        "title": listing.title,
        "org": listing.org,
        "type": listing.type.value if hasattr(listing.type, "value") else listing.type,
        "skills": listing.skills or [],
        "description": listing.description,
    }


def _extract_and_store_deadline(db: Session, listing: NormalizedListing, *, use_llm: bool) -> None:
    text = listing.description or listing.title or ""
    result = extract_deadline(text, use_llm=use_llm)
    db.add(
        Deadline(
            listing_id=listing.id,
            kind=DeadlineKind(result.kind),
            resolved_date=result.resolved_date,
            anchor_text=result.anchor_text,
            raw_phrase=result.raw_phrase,
            confidence=result.confidence,
            needs_review=result.needs_review,
            extractor=Extractor(result.extractor),
        )
    )


def _record_health(source: OpportunitySource, *, ok: bool, created: int = 0, errors: int = 0) -> None:
    health = dict(source.health_json or {})
    runs = health.get("runs", 0) + 1
    ok_runs = health.get("ok_runs", 0) + (1 if ok else 0)
    health.update(
        {
            "runs": runs,
            "ok_runs": ok_runs,
            "success_rate": round(ok_runs / runs, 3),
            "last_ok": ok,
            "last_created": created,
            "last_errors": errors,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "consecutive_failures": 0 if ok else health.get("consecutive_failures", 0) + 1,
        }
    )
    if health["consecutive_failures"] >= 5:
        source.enabled = False  # auto-disable a flapping source
    source.health_json = health


def dedup_all(db: Session) -> dict:
    """Cluster + merge duplicates across all normalized listings."""
    listings = list(db.execute(select(NormalizedListing)).scalars())
    if not listings:
        return {"clusters": 0, "listings": 0}

    source_keys = {
        s.id: s.key for s in db.execute(select(OpportunitySource)).scalars()
    }
    as_dicts = {
        str(ls.id): {
            "id": str(ls.id),
            "url": ls.url,
            "title": ls.title,
            "org": ls.org,
            "skills": ls.skills or [],
            "posted_at": ls.posted_at.isoformat() if ls.posted_at else None,
            "description": ls.description,
            "source_key": source_keys.get(ls.source_id),
        }
        for ls in listings
    }

    pairs = candidate_pairs(list(as_dicts.values()))
    dup_pairs = [
        (a, b) for a, b in pairs if is_duplicate(pair_score(as_dicts[a], as_dicts[b]))
    ]
    clusters = [c for c in cluster_pairs(dup_pairs) if len(c) > 1]

    # reset prior clustering
    for ls in listings:
        ls.cluster_id = None
        ls.is_canonical = True

    by_id = {str(ls.id): ls for ls in listings}
    n_clusters = 0
    for members in clusters:
        member_dicts = [as_dicts[m] for m in members]
        canonical_id = choose_canonical(member_dicts)
        cl = DedupCluster(
            canonical_listing_id=by_id[canonical_id].id,
            member_ids=[by_id[m].id for m in members],
            method_json={"method": "url+fuzzy"},
            confidence=0.9,
            merged_metadata_json=merge_metadata(member_dicts),
        )
        db.add(cl)
        db.flush()
        for m in members:
            ls = by_id[m]
            ls.cluster_id = cl.id
            ls.is_canonical = str(ls.id) == canonical_id
        n_clusters += 1

    db.commit()
    return {"clusters": n_clusters, "listings": len(listings)}
