"""
Learner Feedback Loop (spec section 21):
USER -> LEARN -> ASSESS -> FEEDBACK -> UPDATE LEARNER MODEL -> REPLAN -> LEARN AGAIN
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.services.util import clamp

VELOCITY_DELTA = {
    "too_easy": 0.08,
    "good": 0.04,
    "already_knew": 0.10,
    "too_difficult": -0.05,
    "not_relevant": -0.02,
    "need_more_practice": -0.03,
}


def record_feedback(db: Session, profile: m.LearnerProfile, item_id: str | None, rating: str, confidence_1_5: int | None) -> None:
    feedback = m.Feedback(profile_id=profile.id, learning_path_item_id=item_id, rating=rating, confidence_1_5=confidence_1_5)
    db.add(feedback)

    # Update learning velocity (spec section 13) — a bounded, AI-derived product metric.
    delta = VELOCITY_DELTA.get(rating, 0.0)
    profile.learning_velocity = clamp((profile.learning_velocity or 0.0) + delta, lo=0.0, hi=1.0)
    profile.engagement_score = clamp((profile.engagement_score or 0.0) + 0.05, lo=0.0, hi=1.0)

    if item_id:
        item = db.query(m.LearningPathItem).filter(m.LearningPathItem.id == item_id).first()
        if item:
            if rating in ("good", "already_knew"):
                item.status = "done"
                db.add(
                    m.Progress(profile_id=profile.id, learning_path_item_id=item_id, event_type="completed", detail={"rating": rating})
                )
            elif rating == "not_relevant":
                item.status = "skipped"
                db.add(
                    m.Progress(profile_id=profile.id, learning_path_item_id=item_id, event_type="skipped", detail={"rating": rating})
                )
            else:
                item.status = "in_progress"

    db.commit()
