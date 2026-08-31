"""
Explanation Engine (spec sections 9, 18, 47).

`explain_journey` produces the "Explain My Journey" narrative. `decision_trace`
turns a recommendation's score breakdown into the safe, high-level checklist
shown in the UI (never raw chain-of-thought — just which named factors
contributed).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.services.career_readiness import compute_career_readiness
from app.services.gap_analyzer import analyze_gaps
from app.services.path_optimizer import estimate_completion_weeks, get_active_path_out

FACTOR_LABELS = {
    "skill_gap_relevance": "Fills a real gap in your skill graph",
    "prerequisite_readiness": "Prerequisites are in place",
    "goal_alignment": "Required by your target role",
    "semantic_similarity": "Matches your stated goal and interests",
    "difficulty_fit": "Matched to your current level",
    "time_fit": "Fits your available time",
    "learner_preference": "Matches your preferred learning format",
}


def decision_trace(score_breakdown: dict[str, float], threshold: float = 0.03) -> list[str]:
    """Only surface factors that meaningfully contributed (spec section 47:
    high-level explanation, not internal reasoning)."""
    contributing = [k for k, v in score_breakdown.items() if v >= threshold]
    return [FACTOR_LABELS[k] for k in contributing if k in FACTOR_LABELS]


def explain_journey(db: Session, profile: m.LearnerProfile) -> str:
    target_role = profile.target_role or "your target role"
    gaps = analyze_gaps(db, profile.id, target_role)
    readiness = compute_career_readiness(db, profile)
    path_out = get_active_path_out(db, profile.id)

    parts = []
    parts.append(
        f"You started this journey aiming to become a **{target_role}**"
        + (f" within about {profile.timeline_weeks} weeks" if profile.timeline_weeks else "")
        + f", with roughly {profile.weekly_hours:.1f} hours/week available."
    )

    if gaps.mastered:
        parts.append(
            f"You already bring strong evidence in {', '.join(i.skill_name for i in gaps.mastered[:5])}, "
            "so your roadmap doesn't re-teach those from scratch."
        )

    if gaps.highest_impact_gaps:
        top_names = ", ".join(i.skill_name for i in gaps.highest_impact_gaps[:3])
        parts.append(
            f"Your biggest current gaps are {top_names} — these were prioritized because they block "
            "the most downstream skills on your path."
        )

    if path_out and path_out.items:
        total_minutes = sum(i.estimated_minutes for i in path_out.items if i.status != "done")
        weeks = estimate_completion_weeks(total_minutes, profile.weekly_hours or 8.0)
        phases = sorted({i.phase_title for i in path_out.items})
        parts.append(
            f"Your roadmap is organized into {len(phases)} phases, moving from foundational skills toward "
            f"production-ready skills, with an estimated {weeks} weeks remaining at your current pace."
        )
        if path_out.replanning_log:
            last = path_out.replanning_log[-1]
            parts.append(f"It was last adapted because: {last.get('reason')}")

    parts.append(
        f"Your AI-estimated career readiness is {readiness.overall:.0f}/100. "
        + (f"The fastest way to raise it is completing: {readiness.fastest_improvement}." if readiness.fastest_improvement else "")
    )

    parts.append(
        "These are AI-estimated proficiency and readiness figures based on the evidence you've generated so "
        "far (course completions, assessments, and projects) — not a certified or scientifically validated measurement."
    )

    return " ".join(parts)
