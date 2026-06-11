"""Ad hoc deadline extraction endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.opportunity import DeadlineExtractRequest, DeadlineOut
from deadline_parser import extract as _extract

router = APIRouter()


@router.post("/extract", response_model=DeadlineOut)
def extract_deadline(payload: DeadlineExtractRequest) -> DeadlineOut:
    try:
        result = _extract(payload.text, use_llm=False)
        return DeadlineOut(
            kind=result.kind,
            resolved_date=result.resolved_date,
            anchor_text=result.anchor_text,
            raw_phrase=result.raw_phrase,
            confidence=result.confidence,
            needs_review=result.needs_review,
            extractor=result.extractor,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
