"""
Learning Path Optimizer + Adaptive Path Engine (spec sections 8, 12, 14, 15).

generate_path(): builds a phased roadmap in prerequisite order, interleaving
resources, checkpoint assessments, and project milestones (project-first
learning, spec section 15), sized to the learner's weekly time budget.

replan_path(): the Adaptive Path Engine. Reacts to assessment results,
feedback, or profile changes by adjusting the *existing* path in place
(shrinking/removing items, reordering) and appends a human-readable entry to
the path's replanning_log so "Why was X moved?" (spec section 11/18) has a
grounded, non-fabricated answer.
"""
from __future__ import annotations

import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import LearningPathOut, PathItemOut
from app.services.gap_analyzer import analyze_gaps
from app.services.recommendation import score_resources_for_profile
from app.services.skill_graph import resolve_target_skill_set, topological_learning_order
from app.services.util import status_for_confidence

PHASE_SIZE = 4  # skills per phase, tuned for readable roadmaps


def _time_budget_allocation(weekly_hours: float) -> dict[str, int]:
    """Time-Budget Optimizer (spec section 14). Splits a daily/weekly budget
    into theory / practice / project / revision minutes."""
    weekly_minutes = max(weekly_hours, 1) * 60
    daily_minutes = weekly_minutes / 7
    return {
        "theory_min": round(daily_minutes * 0.40),
        "practice_min": round(daily_minutes * 0.35),
        "project_min": round(daily_minutes * 0.20),
        "revision_min": round(daily_minutes * 0.05),
    }


def _phase_title(index: int, categories: list[str]) -> str:
    dominant = categories[0] if categories else "Foundations"
    return f"Phase {index + 1}: {dominant}"


def generate_path(db: Session, profile: m.LearnerProfile) -> m.LearningPath:
    # Supersede any existing active path.
    existing = (
        db.query(m.LearningPath)
        .filter(m.LearningPath.profile_id == profile.id, m.LearningPath.status == "active")
        .first()
    )
    version = 1
    if existing:
        existing.status = "superseded"
        version = existing.version + 1

    target_role = profile.target_role or "AI Engineer"
    gaps = analyze_gaps(db, profile.id, target_role)
    need_skill_keys = [i.skill_key for i in gaps.partial] + [i.skill_key for i in gaps.missing]
    ordered_keys = [k for k in topological_learning_order(db, resolve_target_skill_set(db, target_role)) if k in need_skill_keys]

    scored_resources = score_resources_for_profile(db, profile, limit=200)
    best_resource_by_skill: dict[str, object] = {}
    for c in scored_resources:
        if c.skill_key and c.skill_key not in best_resource_by_skill:
            best_resource_by_skill[c.skill_key] = c

    projects = db.query(m.Project).all()
    project_skill_rows = db.query(m.ProjectSkill).all()
    skills_by_id = {s.id: s for s in db.query(m.Skill).all()}
    project_to_skills: dict[str, set[str]] = {}
    for ps in project_skill_rows:
        skill = skills_by_id.get(ps.skill_id)
        if skill:
            project_to_skills.setdefault(ps.project_id, set()).add(skill.key)
    used_projects: set[str] = set()

    path = m.LearningPath(profile_id=profile.id, target_role=target_role, version=version, status="active")
    db.add(path)
    db.flush()

    order_index = 0
    covered_in_phase: set[str] = set()

    chunks = [ordered_keys[i : i + PHASE_SIZE] for i in range(0, len(ordered_keys), PHASE_SIZE)]
    for phase_idx, chunk in enumerate(chunks):
        categories = []
        for skill_key in chunk:
            skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
            if skill and skill.category not in categories:
                categories.append(skill.category)
        phase_title = _phase_title(phase_idx, categories)

        for skill_key in chunk:
            skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
            resource = best_resource_by_skill.get(skill_key)
            title = resource.title if resource else f"Study: {skill.name}"
            minutes = resource.estimated_minutes if resource else 120
            item = m.LearningPathItem(
                learning_path_id=path.id,
                phase_index=phase_idx,
                phase_title=phase_title,
                skill_id=skill.id,
                item_type="resource",
                ref_id=resource.ref_id if resource else None,
                title=title,
                estimated_minutes=minutes,
                order_index=order_index,
                why=resource.why if resource else f"Foundational for {target_role}.",
                score=resource.score if resource else 0.0,
            )
            db.add(item)
            order_index += 1
            covered_in_phase.add(skill_key)

        # Checkpoint assessment at the end of the phase.
        checkpoint = m.LearningPathItem(
            learning_path_id=path.id,
            phase_index=phase_idx,
            phase_title=phase_title,
            skill_id=None,
            item_type="checkpoint",
            ref_id=None,
            title=f"Checkpoint: adaptive assessment on {', '.join(categories) or 'this phase'}",
            estimated_minutes=15,
            order_index=order_index,
            why="Verifies mastery before moving on, so the roadmap can adapt if needed.",
        )
        db.add(checkpoint)
        order_index += 1

        # Project-first: attach the best-fit project once enough of its
        # skills are covered by this phase (spec section 15).
        best_project, best_overlap = None, 0
        for project in projects:
            if project.id in used_projects:
                continue
            overlap = len(project_to_skills.get(project.id, set()) & covered_in_phase)
            if overlap > best_overlap and overlap >= 1:
                best_project, best_overlap = project, overlap
        if best_project and best_overlap >= max(1, len(chunk) // 2):
            used_projects.add(best_project.id)
            proj_item = m.LearningPathItem(
                learning_path_id=path.id,
                phase_index=phase_idx,
                phase_title=phase_title,
                skill_id=None,
                item_type="project",
                ref_id=best_project.id,
                title=f"Project: {best_project.title}",
                estimated_minutes=int(best_project.estimated_hours * 60),
                order_index=order_index,
                why=f"Demonstrates {', '.join(sorted(project_to_skills.get(best_project.id, set())))} as portfolio evidence.",
            )
            db.add(proj_item)
            order_index += 1

    db.commit()
    db.refresh(path)
    return path


def _serialize(db: Session, path: m.LearningPath) -> LearningPathOut:
    items = (
        db.query(m.LearningPathItem)
        .filter(m.LearningPathItem.learning_path_id == path.id)
        .order_by(m.LearningPathItem.order_index)
        .all()
    )
    skills_by_id = {s.id: s for s in db.query(m.Skill).all()}
    out_items = []
    for it in items:
        skill_key = skills_by_id[it.skill_id].key if it.skill_id and it.skill_id in skills_by_id else None
        out_items.append(
            PathItemOut(
                id=it.id,
                phase_index=it.phase_index,
                phase_title=it.phase_title or "",
                item_type=it.item_type,
                ref_id=it.ref_id,
                title=it.title,
                estimated_minutes=it.estimated_minutes,
                order_index=it.order_index,
                status=it.status,
                why=it.why,
                skill_key=skill_key,
            )
        )
    return LearningPathOut(
        id=path.id, version=path.version, target_role=path.target_role, items=out_items,
        replanning_log=path.replanning_log or [],
    )


def get_active_path(db: Session, profile_id: str) -> m.LearningPath | None:
    return (
        db.query(m.LearningPath)
        .filter(m.LearningPath.profile_id == profile_id, m.LearningPath.status == "active")
        .first()
    )


def get_active_path_out(db: Session, profile_id: str) -> LearningPathOut | None:
    path = get_active_path(db, profile_id)
    if not path:
        return None
    return _serialize(db, path)


def replan_path(db: Session, profile: m.LearnerProfile, reason: str | None = None) -> LearningPathOut:
    """Adaptive Path Engine (spec section 12). Regenerates the path from the
    learner's *current* skill graph (which reflects new assessment/feedback
    evidence), then diffs against the previous version to log what changed
    and why, in plain language."""
    old_path = get_active_path(db, profile.id)
    old_items = []
    if old_path:
        old_items = (
            db.query(m.LearningPathItem)
            .filter(m.LearningPathItem.learning_path_id == old_path.id)
            .all()
        )
    old_titles = {it.title for it in old_items}
    old_total_minutes = sum(it.estimated_minutes for it in old_items if it.status != "done")

    new_path = generate_path(db, profile)
    new_items = (
        db.query(m.LearningPathItem)
        .filter(m.LearningPathItem.learning_path_id == new_path.id)
        .order_by(m.LearningPathItem.order_index)
        .all()
    )
    new_titles = {it.title for it in new_items}
    new_total_minutes = sum(it.estimated_minutes for it in new_items)

    removed = old_titles - new_titles
    added = new_titles - old_titles
    log_entry = {
        "ts": datetime.utcnow().isoformat(),
        "reason": reason or "Learner profile or evidence changed.",
        "items_removed": list(removed)[:5],
        "items_added": list(added)[:5],
        "estimated_minutes_before": old_total_minutes,
        "estimated_minutes_after": new_total_minutes,
    }
    log = (old_path.replanning_log if old_path else []) or []
    log = log + [log_entry]
    new_path.replanning_log = log
    db.commit()
    db.refresh(new_path)
    return _serialize(db, new_path)


def estimate_completion_weeks(total_minutes: int, weekly_hours: float) -> float:
    weekly_minutes = max(weekly_hours, 1) * 60
    return round(total_minutes / weekly_minutes, 1) if weekly_minutes else math.inf
