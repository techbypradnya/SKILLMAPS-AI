from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import DashboardOut, PathItemOut, RecommendationOut
from app.services.career_readiness import compute_career_readiness
from app.services.gap_analyzer import analyze_gaps
from app.services.path_optimizer import get_active_path_out
from app.services.recommendation import score_resources_for_profile, to_out


def build_dashboard(db: Session, profile: m.LearnerProfile) -> DashboardOut:
    gaps = analyze_gaps(db, profile.id, profile.target_role or "AI Engineer")
    readiness = compute_career_readiness(db, profile)
    path_out = get_active_path_out(db, profile.id)

    all_items = path_out.items if path_out else []
    done = [i for i in all_items if i.status == "done"]
    overall_progress = round(100 * len(done) / len(all_items), 1) if all_items else 0.0
    current_phase = next((i.phase_title for i in all_items if i.status != "done"), (all_items[-1].phase_title if all_items else None))

    next_best: RecommendationOut | None = None
    candidates = score_resources_for_profile(db, profile, limit=1)
    if candidates:
        next_best = to_out(candidates[0])

    today_items: list[PathItemOut] = [i for i in all_items if i.status == "pending"][:4]

    skill_summary = {"mastered": len(gaps.mastered), "developing": len(gaps.partial), "missing": len(gaps.missing)}

    return DashboardOut(
        profile_id=profile.id,
        target_role=profile.target_role,
        overall_progress=overall_progress,
        current_phase=current_phase,
        learning_velocity=round(profile.learning_velocity or 0.0, 2),
        career_readiness=readiness,
        next_best_action=next_best,
        today_mission=today_items,
        skill_summary=skill_summary,
    )
