"""
Career Readiness Score (spec section 16). An AI-estimated readiness rollup
across skill mastery, projects, and deployment/production skills — always
explicitly labeled as an estimate, never a guarantee.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import CareerReadinessOut
from app.services.gap_analyzer import analyze_gaps
from app.services.skill_graph import resolve_target_skill_set

CATEGORY_GROUPS = {
    "Technical Skills": {"Programming", "Data", "Mathematics", "Machine Learning", "Deep Learning", "Frontend", "Backend", "Security"},
    "GenAI": {"Generative AI"},
    "Deployment": {"Production AI"},
    "Problem Solving": {"Machine Learning", "Deep Learning"},
}


def compute_career_readiness(db: Session, profile: m.LearnerProfile) -> CareerReadinessOut:
    target_role = profile.target_role or "AI Engineer"
    gaps = analyze_gaps(db, profile.id, target_role)
    all_items = gaps.mastered + gaps.partial + gaps.missing
    skills_by_key = {s.key: s for s in db.query(m.Skill).all()}

    breakdown: dict[str, float] = {}
    for group_name, categories in CATEGORY_GROUPS.items():
        relevant = [i for i in all_items if i.category in categories]
        if not relevant:
            continue
        breakdown[group_name] = round(sum(i.confidence for i in relevant) / len(relevant), 1)

    # Projects component: proportion of role-relevant projects with at least
    # partial skill coverage that the learner has decent confidence in.
    projects = db.query(m.Project).all()
    project_skill_rows = db.query(m.ProjectSkill).all()
    id_to_key = {s.id: k for k, s in skills_by_key.items()}
    project_to_skills = {}
    for ps in project_skill_rows:
        key = id_to_key.get(ps.skill_id)
        if key:
            project_to_skills.setdefault(ps.project_id, []).append(key)

    target_keys = set(resolve_target_skill_set(db, target_role))
    conf_by_key = {i.skill_key: i.confidence for i in all_items}
    relevant_projects = [p for p in projects if set(project_to_skills.get(p.id, [])) & target_keys]
    if relevant_projects:
        readiness_scores = []
        for p in relevant_projects:
            skills = project_to_skills.get(p.id, [])
            if not skills:
                continue
            avg_conf = sum(conf_by_key.get(k, 0) for k in skills) / len(skills)
            readiness_scores.append(avg_conf)
        breakdown["Projects"] = round(sum(readiness_scores) / len(readiness_scores), 1) if readiness_scores else 0.0
    else:
        breakdown["Projects"] = 0.0

    overall = round(sum(breakdown.values()) / len(breakdown), 1) if breakdown else 0.0

    blockers = [i.skill_name for i in sorted(gaps.missing, key=lambda x: -x.gap_score)[:3]]
    fastest = None
    if gaps.highest_impact_gaps:
        fastest = gaps.highest_impact_gaps[0].skill_name

    return CareerReadinessOut(overall=overall, breakdown=breakdown, blockers=blockers, fastest_improvement=fastest)
