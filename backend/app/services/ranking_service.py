"""Ranking service: compute explainable rank scores, build feed + explanation.

Retrieval/scoring run in Python over stored vectors (portable across pgvector
and SQLite). Per-user component weights come from settings and are nudged by the
feedback loop. Every score keeps its component breakdown for explainability.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deadline import Deadline
from app.models.embedding import Embedding
from app.models.enums import EmbeddingOwner
from app.models.listing import DedupCluster, NormalizedListing
from app.models.ranking import RankScore
from app.models.user import User, UserProfile
from app.services.embeddings import get_listing_vectors
from ranking import features
from ranking.learning import default_weights
from ranking.retriever import cosine
from ranking.scorer import blend

MODEL_VERSION = "v1"


def _profile_for_user(db: Session, user_id: uuid.UUID) -> UserProfile | None:
    return db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).scalar_one_or_none()


def _profile_vectors(db: Session, profile_id: uuid.UUID) -> list[list[float]]:
    rows = db.execute(
        select(Embedding).where(
            Embedding.owner_type == EmbeddingOwner.profile,
            Embedding.owner_id == profile_id,
        )
    ).scalars()
    return [[float(x) for x in r.vector] for r in rows]


def get_weights(db: Session, user: User) -> dict[str, float]:
    return dict((user.settings_json or {}).get("rank_weights") or default_weights())


def _latest_deadline(db: Session, listing_id: uuid.UUID) -> Deadline | None:
    return db.execute(
        select(Deadline)
        .where(Deadline.listing_id == listing_id)
        .order_by(Deadline.created_at.desc())
    ).scalars().first()


def rank_user(db: Session, user_id: uuid.UUID) -> int:
    """(Re)compute rank_scores for a user across canonical listings."""
    user = db.get(User, user_id)
    profile = _profile_for_user(db, user_id)
    if user is None or profile is None:
        raise KeyError("user/profile not found")

    pvecs = _profile_vectors(db, profile.id)
    profile_skills = [s.canonical_name for s in profile.skills]
    weights = get_weights(db, user)
    now = datetime.now(timezone.utc)

    listings = list(
        db.execute(select(NormalizedListing).where(NormalizedListing.is_canonical.is_(True))).scalars()
    )
    vectors = get_listing_vectors(db, [ls.id for ls in listings])

    # clear previous scores for this user+model
    for old in db.execute(
        select(RankScore).where(
            RankScore.user_id == user_id, RankScore.model_version == MODEL_VERSION
        )
    ).scalars():
        db.delete(old)
    db.flush()

    for ls in listings:
        lvec = vectors.get(str(ls.id))
        semantic = max((cosine(p, lvec) for p in pvecs), default=0.0) if lvec else 0.0
        semantic = max(0.0, semantic)
        skill_score, matched = features.skill_overlap(profile_skills, ls.skills or [])
        rec = features.recency(ls.posted_at, now)
        dl = _latest_deadline(db, ls.id)
        urg = features.urgency(
            dl.kind.value if dl else None, dl.resolved_date if dl else None, now
        )
        components = {
            "semantic": round(semantic, 4),
            "skill_overlap": round(skill_score, 4),
            "recency": round(rec, 4),
            "urgency": round(urg, 4),
            "feedback": 0.0,
        }
        score, _ = blend(components, weights)
        db.add(
            RankScore(
                user_id=user_id,
                listing_id=ls.id,
                score=round(score, 6),
                components_json=components,
                matched_skills=matched,
                model_version=MODEL_VERSION,
                computed_at=now,
            )
        )
    db.commit()
    return len(listings)


def _also_seen_on(db: Session, listing: NormalizedListing) -> list[str]:
    if not listing.cluster_id:
        return []
    cl = db.get(DedupCluster, listing.cluster_id)
    if not cl:
        return []
    urls = (cl.merged_metadata_json or {}).get("source_urls", [])
    return [u for u in urls if u != listing.url]


def _deadline_out(dl: Deadline | None) -> dict | None:
    if dl is None:
        return None
    return {
        "kind": dl.kind.value,
        "resolved_date": dl.resolved_date,
        "anchor_text": dl.anchor_text,
        "raw_phrase": dl.raw_phrase,
        "confidence": dl.confidence,
        "needs_review": dl.needs_review,
        "extractor": dl.extractor.value if dl.extractor else None,
    }


def get_feed(
    db: Session,
    user_id: uuid.UUID | None = None,
    *,
    type_filter: str | None = None,
    remote: bool | None = None,
    deadline_before: datetime | None = None,
    q: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict], int]:
    """Return (items, total) for the feed, ranked by score when available."""
    scores = {}
    if user_id is not None:
        scores = {
            rs.listing_id: rs
            for rs in db.execute(
                select(RankScore).where(
                    RankScore.user_id == user_id, RankScore.model_version == MODEL_VERSION
                )
            ).scalars()
        }
    listings = list(
        db.execute(select(NormalizedListing).where(NormalizedListing.is_canonical.is_(True))).scalars()
    )

    rows: list[dict] = []
    for ls in listings:
        if type_filter and ls.type.value != type_filter:
            continue
        if remote is not None and ls.is_remote != remote:
            continue
        if q and q.lower() not in f"{ls.title} {ls.description or ''}".lower():
            continue
        dl = _latest_deadline(db, ls.id)
        if deadline_before and dl and dl.resolved_date and dl.resolved_date > deadline_before:
            continue
        rs = scores.get(ls.id)
        rows.append(
            {
                "id": ls.id,
                "title": ls.title,
                "org": ls.org,
                "type": ls.type.value,
                "location": ls.location,
                "is_remote": ls.is_remote,
                "url": ls.url,
                "posted_at": ls.posted_at,
                "skills": ls.skills or [],
                "score": round(rs.score, 4) if rs else None,
                "deadline": _deadline_out(dl),
                "also_seen_on": _also_seen_on(db, ls),
            }
        )

    rows.sort(key=lambda r: (r["score"] is not None, r["score"] or 0.0), reverse=True)
    total = len(rows)
    start = (page - 1) * limit
    return rows[start : start + limit], total


def get_opportunity(db: Session, listing_id: uuid.UUID, user_id: uuid.UUID | None = None) -> dict | None:
    ls = db.get(NormalizedListing, listing_id)
    if ls is None:
        return None
    rs = None
    if user_id:
        rs = db.execute(
            select(RankScore).where(
                RankScore.user_id == user_id,
                RankScore.listing_id == listing_id,
                RankScore.model_version == MODEL_VERSION,
            )
        ).scalar_one_or_none()
    return {
        "id": ls.id,
        "title": ls.title,
        "org": ls.org,
        "type": ls.type.value,
        "location": ls.location,
        "is_remote": ls.is_remote,
        "url": ls.url,
        "posted_at": ls.posted_at,
        "skills": ls.skills or [],
        "score": round(rs.score, 4) if rs else None,
        "deadline": _deadline_out(_latest_deadline(db, ls.id)),
        "also_seen_on": _also_seen_on(db, ls),
    }


def get_explanation(db: Session, listing_id: uuid.UUID, user_id: uuid.UUID) -> dict | None:
    rs = db.execute(
        select(RankScore).where(
            RankScore.user_id == user_id,
            RankScore.listing_id == listing_id,
            RankScore.model_version == MODEL_VERSION,
        )
    ).scalar_one_or_none()
    if rs is None:
        return None
    return {
        "listing_id": rs.listing_id,
        "score": round(rs.score, 4),
        "components": rs.components_json,
        "matched_skills": rs.matched_skills or [],
        "model_version": rs.model_version,
    }
