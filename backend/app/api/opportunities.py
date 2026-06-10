"""Opportunity search, detail, and ranking-explanation endpoints.

Reads precomputed rank_scores (search/detail stay fast and synchronous).
TODO(phase-1/2): implement search over normalized_listings + rank_scores and
the explanation payload from components_json.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import OpportunityType
from app.schemas.common import Page
from app.schemas.opportunity import ExplanationOut, OpportunityOut

router = APIRouter()


@router.get("", response_model=Page[OpportunityOut])
def search_opportunities(
    q: str | None = None,
    intent: str | None = None,
    type: OpportunityType | None = None,
    location: str | None = None,
    remote: bool | None = None,
    deadline_before: datetime | None = None,
    sort: str = "score",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Page[OpportunityOut]:
    raise HTTPException(status_code=501, detail="TODO(phase-1): search_opportunities")


@router.get("/{listing_id}", response_model=OpportunityOut)
def get_opportunity(listing_id: uuid.UUID) -> OpportunityOut:
    raise HTTPException(status_code=501, detail="TODO(phase-1): get_opportunity")


@router.get("/{listing_id}/explanation", response_model=ExplanationOut)
def explain_opportunity(listing_id: uuid.UUID, user_id: uuid.UUID) -> ExplanationOut:
    raise HTTPException(status_code=501, detail="TODO(phase-2): explain_opportunity")
