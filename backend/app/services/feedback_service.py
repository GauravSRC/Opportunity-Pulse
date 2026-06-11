"""Feedback service: persist signals, nudge ranking weights, re-rank."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import FeedbackSignal
from app.models.feedback import Feedback
from app.models.ranking import RankScore
from app.models.user import User
from app.services import ranking_service
from ranking.learning import update_weights

_SIGNAL_WEIGHT = {
    "save": 1.0, "applied": 1.5, "thumbs_up": 1.0,
    "click": 0.3, "dismiss": 1.0, "thumbs_down": 1.0,
}


def submit(db: Session, payload) -> dict:
    """payload: app.schemas.feedback.FeedbackIn. Returns updated weights."""
    user = db.get(User, payload.user_id)
    if user is None:
        raise KeyError("user not found")

    db.add(
        Feedback(
            user_id=payload.user_id,
            listing_id=payload.listing_id,
            signal=FeedbackSignal(payload.signal.value),
            weight=_SIGNAL_WEIGHT.get(payload.signal.value, 1.0),
            context_json=payload.context or {},
        )
    )

    # attribute credit/blame using the components the user reacted to
    rs = db.execute(
        select(RankScore).where(
            RankScore.user_id == payload.user_id,
            RankScore.listing_id == payload.listing_id,
            RankScore.model_version == ranking_service.MODEL_VERSION,
        )
    ).scalar_one_or_none()
    components = rs.components_json if rs else {}

    weights = ranking_service.get_weights(db, user)
    new_weights = update_weights(weights, payload.signal.value, components)
    settings = dict(user.settings_json or {})
    settings["rank_weights"] = new_weights
    user.settings_json = settings
    db.commit()

    # cheap re-rank so the feed reflects the updated preferences (MVP scale)
    ranking_service.rank_user(db, payload.user_id)
    return {"ok": True, "weights": new_weights}
