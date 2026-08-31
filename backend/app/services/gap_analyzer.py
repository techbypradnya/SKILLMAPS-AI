"""
Skill Gap Analysis (spec section 6).

Compares the learner's current skill graph against the target role's skill
graph and produces mastered / partial / missing buckets plus a
highest-impact-gap ranking that accounts for both the size of the gap and
how many downstream (dependent) skills are blocked by it.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import GapAnalysisOut, SkillGapItem
from app.services.skill_graph import (
    build_full_graph,
    get_dependents,
    learner_skill_map,
    resolve_target_skill_set,
)


def analyze_gaps(db: Session, profile_id: str, target_role: str) -> GapAnalysisOut:
    target_keys = resolve_target_skill_set(db, target_role)
    graph = build_full_graph(db)
    learner_skills = learner_skill_map(db, profile_id)
    skills_by_key = {s.key: s for s in db.query(m.Skill).all()}

    mastered, partial, missing = [], [], []

    for key in target_keys:
        skill = skills_by_key.get(key)
        if not skill:
            continue
        ls = learner_skills.get(key)
        confidence = ls.confidence if ls else 0.0
        status = ls.status if ls else "unknown"

        # blocked_by: direct prerequisites that are NOT yet proficient (>=60)
        blocked_by = []
        if key in graph:
            for prereq in graph.successors(key):
                prereq_ls = learner_skills.get(prereq)
                prereq_conf = prereq_ls.confidence if prereq_ls else 0.0
                if prereq_conf < 60 and prereq in target_keys:
                    blocked_by.append(prereq)

        gap_score = round(100 - confidence, 1)

        item = SkillGapItem(
            skill_key=key,
            skill_name=skill.name,
            category=skill.category,
            confidence=confidence,
            status=status,
            gap_score=gap_score,
            blocked_by=blocked_by,
        )

        if confidence >= 70:
            mastered.append(item)
        elif confidence >= 30:
            partial.append(item)
        else:
            missing.append(item)

    # Highest-impact gaps: weight the raw gap by how many *other* target
    # skills depend on this one (unblocking downstream skills), and
    # penalize skills that are still blocked by unmet prerequisites of
    # their own (those aren't "ready" to tackle yet).
    impact_pool = partial + missing
    scored = []
    for item in impact_pool:
        dependents = [d for d in get_dependents(db, item.skill_key) if d in target_keys]
        readiness_penalty = 15 * len(item.blocked_by)
        impact = item.gap_score + 6 * len(dependents) - readiness_penalty
        scored.append((impact, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    highest_impact = []
    for rank, (_, item) in enumerate(scored[:5], start=1):
        item.priority_rank = rank
        highest_impact.append(item)

    return GapAnalysisOut(mastered=mastered, partial=partial, missing=missing, highest_impact_gaps=highest_impact)
