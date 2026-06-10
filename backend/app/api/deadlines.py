"""Ad hoc deadline extraction endpoint.

TODO(phase-3): call deadline_parser ladder (rules -> ner -> llm) and return the
structured result with confidence.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.opportunity import DeadlineExtractRequest, DeadlineOut

router = APIRouter()


@router.post("/extract", response_model=DeadlineOut)
def extract_deadline(payload: DeadlineExtractRequest) -> DeadlineOut:
    raise HTTPException(status_code=501, detail="TODO(phase-3): extract_deadline")
