"""Opportunity search, detail, ranking-explanation, and ad hoc score endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import OpportunityType
from app.schemas.common import Page
from app.schemas.opportunity import DeadlineOut, ExplanationOut, OpportunityOut, ScoreComponents
from app.services import ranking_service

router = APIRouter()


def _dl_out(dl: dict | None) -> DeadlineOut | None:
    if dl is None:
        return None
    return DeadlineOut(
        kind=dl["kind"],
        resolved_date=dl.get("resolved_date"),
        anchor_text=dl.get("anchor_text"),
        raw_phrase=dl.get("raw_phrase"),
        confidence=dl.get("confidence", 0.0),
        needs_review=dl.get("needs_review", False),
        extractor=dl.get("extractor"),
    )


def _row_to_out(row: dict) -> OpportunityOut:
    return OpportunityOut(
        id=row["id"],
        title=row["title"],
        org=row.get("org"),
        type=row["type"],
        location=row.get("location"),
        is_remote=bool(row.get("is_remote", False)),
        url=row["url"],
        posted_at=row.get("posted_at"),
        skills=row.get("skills", []),
        score=row.get("score"),
        deadline=_dl_out(row.get("deadline")),
        also_seen_on=row.get("also_seen_on", []),
    )


@router.get("", response_model=Page[OpportunityOut])
def search_opportunities(
    q: str | None = None,
    intent: str | None = None,
    type: OpportunityType | None = None,
    location: str | None = None,
    remote: bool | None = None,
    deadline_before: datetime | None = None,
    user_id: uuid.UUID | None = None,
    sort: str = "score",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Page[OpportunityOut]:
    items, total = ranking_service.get_feed(
        db,
        user_id=user_id,
        type_filter=type.value if type else None,
        remote=remote,
        deadline_before=deadline_before,
        q=q,
        page=page,
        limit=limit,
    )
    return Page(
        items=[_row_to_out(r) for r in items],
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{listing_id}", response_model=OpportunityOut)
def get_opportunity(
    listing_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> OpportunityOut:
    row = ranking_service.get_opportunity(db, listing_id, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return _row_to_out(row)


@router.get("/{listing_id}/explanation", response_model=ExplanationOut)
def explain_opportunity(
    listing_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ExplanationOut:
    result = ranking_service.get_explanation(db, listing_id, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No rank score found for this user/listing")
    comps = result["components"]
    return ExplanationOut(
        listing_id=result["listing_id"],
        score=result["score"],
        components=ScoreComponents(
            semantic=comps.get("semantic", 0.0),
            skill_overlap=comps.get("skill_overlap", 0.0),
            recency=comps.get("recency", 0.0),
            urgency=comps.get("urgency", 0.0),
            feedback=comps.get("feedback", 0.0),
        ),
        matched_skills=result.get("matched_skills", []),
        model_version=result["model_version"],
    )


@router.post("/{listing_id}/score")
def adhoc_score(
    listing_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Ad hoc match score for the Chrome extension — runs ranking for this single listing."""
    row = ranking_service.get_opportunity(db, listing_id, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    expl = ranking_service.get_explanation(db, listing_id, user_id)
    if expl is None:
        # Compute on demand if no precomputed score exists
        try:
            ranking_service.rank_user(db, user_id)
            expl = ranking_service.get_explanation(db, listing_id, user_id)
        except KeyError:
            pass
    return {
        "listing_id": listing_id,
        "score": expl["score"] if expl else None,
        "components": expl["components"] if expl else {},
        "matched_skills": expl.get("matched_skills", []) if expl else [],
    }
