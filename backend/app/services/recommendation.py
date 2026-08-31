"""
Recommendation Engine (spec sections 7, 9, 30).

Hybrid scoring: content-based + semantic similarity + prerequisite graph +
learner proficiency + difficulty + time constraints + preference feedback.
Weights are explicit, configurable heuristics — NOT claimed to be
scientifically optimal (spec section 30) — and are designed to later be
learned from the feedback loop (spec section 21).
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import RecommendationOut
from app.services.skill_graph import build_full_graph, learner_skill_map, resolve_target_skill_set
from app.services.vector_store import similarity_scores

DEFAULT_WEIGHTS = {
    "skill_gap_relevance": 0.30,
    "prerequisite_readiness": 0.20,
    "goal_alignment": 0.15,
    "semantic_similarity": 0.10,
    "difficulty_fit": 0.10,
    "time_fit": 0.10,
    "learner_preference": 0.05,
}

DIFFICULTY_RANK = {"beginner": 0, "developing": 0, "intermediate": 1, "advanced": 2}
CONFIDENCE_BAND_TO_DIFFICULTY_RANK = {"unknown": 0, "beginner": 0, "developing": 0.5, "proficient": 1.5, "strong": 2}


@dataclass
class ScoredCandidate:
    ref_type: str
    ref_id: str
    title: str
    skill_key: str | None
    score: float
    breakdown: dict[str, float]
    why: str
    difficulty: str | None = None
    estimated_minutes: int | None = None
    url: str | None = None


def _difficulty_fit(resource_difficulty: str, learner_band: str) -> float:
    r = DIFFICULTY_RANK.get(resource_difficulty, 1)
    l = CONFIDENCE_BAND_TO_DIFFICULTY_RANK.get(learner_band, 0.5)
    distance = abs(r - l)
    return max(0.0, 1 - distance / 2)


def _time_fit(estimated_minutes: int, weekly_hours: float) -> float:
    weekly_minutes = max(weekly_hours, 1) * 60
    # A single resource shouldn't eat the whole weekly budget.
    ratio = estimated_minutes / weekly_minutes
    if ratio <= 0.35:
        return 1.0
    if ratio >= 1.2:
        return 0.1
    return max(0.1, 1 - (ratio - 0.35) / 0.85)


def _preference_fit(resource_type: str, preferences: list[str]) -> float:
    mapping = {
        "project-first": {"exercise", "course"},
        "video": {"video"},
        "reading": {"article", "doc", "book"},
    }
    for pref in preferences or []:
        if resource_type in mapping.get(pref, set()):
            return 1.0
    return 0.5  # neutral if no explicit preference matches


def score_resources_for_profile(
    db: Session, profile: m.LearnerProfile, limit: int = 20, weights: dict[str, float] | None = None
) -> list[ScoredCandidate]:
    weights = weights or DEFAULT_WEIGHTS
    target_keys = set(resolve_target_skill_set(db, profile.target_role or "AI Engineer"))
    graph = build_full_graph(db)
    learner_skills = learner_skill_map(db, profile.id)
    skills_by_key = {s.key: s for s in db.query(m.Skill).all()}
    skills_by_id = {s.id: s for s in db.query(m.Skill).all()}

    resources = db.query(m.Resource).all()
    resource_skill_rows = db.query(m.ResourceSkill).all()
    resource_to_skills: dict[str, list[str]] = {}
    for rs in resource_skill_rows:
        skill = skills_by_id.get(rs.skill_id)
        if skill:
            resource_to_skills.setdefault(rs.resource_id, []).append(skill.key)

    goal_text = f"{profile.goal_raw_text or ''} {profile.target_role or ''} {' '.join(profile.interests or [])}"
    resource_titles = [r.title for r in resources]
    sem_scores = similarity_scores(goal_text, resource_titles) if goal_text.strip() else [0.0] * len(resources)

    candidates: list[ScoredCandidate] = []
    for resource, sem_score in zip(resources, sem_scores):
        taught_skills = [k for k in resource_to_skills.get(resource.id, []) if k in target_keys]
        if not taught_skills:
            continue  # only recommend resources relevant to the learner's target role

        # Pick the skill with the largest gap as the "primary" skill this recommendation targets.
        best_skill_key, best_gap, best_conf, best_status = None, -1.0, 0.0, "unknown"
        for key in taught_skills:
            ls = learner_skills.get(key)
            conf = ls.confidence if ls else 0.0
            gap = 100 - conf
            if gap > best_gap:
                best_skill_key, best_gap, best_conf, best_status = key, gap, conf, (ls.status if ls else "unknown")

        if best_conf >= 85:
            continue  # already strong here, don't recommend again

        skill_gap_relevance = best_gap / 100.0

        prereqs = list(graph.successors(best_skill_key)) if best_skill_key in graph else []
        if prereqs:
            prereq_confs = [
                (learner_skills.get(p).confidence if learner_skills.get(p) else 0.0) for p in prereqs
            ]
            prerequisite_readiness = sum(prereq_confs) / (100.0 * len(prereq_confs))
        else:
            prerequisite_readiness = 1.0

        goal_alignment = 1.0  # already filtered to target_keys; could weight core vs transitive later
        difficulty_fit = _difficulty_fit(resource.difficulty, best_status)
        time_fit = _time_fit(resource.estimated_minutes, profile.weekly_hours or 8.0)
        preference_fit = _preference_fit(resource.resource_type, profile.learning_preferences or [])

        breakdown = {
            "skill_gap_relevance": round(skill_gap_relevance * weights["skill_gap_relevance"], 4),
            "prerequisite_readiness": round(prerequisite_readiness * weights["prerequisite_readiness"], 4),
            "goal_alignment": round(goal_alignment * weights["goal_alignment"], 4),
            "semantic_similarity": round(sem_score * weights["semantic_similarity"], 4),
            "difficulty_fit": round(difficulty_fit * weights["difficulty_fit"], 4),
            "time_fit": round(time_fit * weights["time_fit"], 4),
            "learner_preference": round(preference_fit * weights["learner_preference"], 4),
        }
        total = round(sum(breakdown.values()), 4)

        # also apply a soft penalty if key prerequisites are badly unmet — nudges
        # the recommender to surface the prerequisite itself instead (handled
        # by the fact the prerequisite resource will independently score high).
        if prerequisite_readiness < 0.35:
            total *= 0.6

        why = _explain(resource.title, skills_by_key[best_skill_key].name, best_status, prereqs, learner_skills, skills_by_key, profile)

        candidates.append(
            ScoredCandidate(
                ref_type="resource",
                ref_id=resource.id,
                title=resource.title,
                skill_key=best_skill_key,
                score=round(total, 4),
                breakdown=breakdown,
                why=why,
                difficulty=resource.difficulty,
                estimated_minutes=resource.estimated_minutes,
                url=resource.url,
            )
        )

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:limit]


def _explain(resource_title, skill_name, learner_status, prereq_keys, learner_skills, skills_by_key, profile) -> str:
    """Rule-based 'Why this?' explanation (spec section 9). Deterministic so
    it never fabricates claims about the learner."""
    reasons = []
    if learner_status in ("unknown", "beginner"):
        reasons.append(f"you have limited evidence of {skill_name.lower()} so far")
    else:
        reasons.append(f"you're still developing {skill_name.lower()}")

    ready_prereqs = [
        skills_by_key[p].name for p in prereq_keys
        if (learner_skills.get(p).confidence if learner_skills.get(p) else 0) >= 60
    ]
    if ready_prereqs:
        reasons.append(f"you already have {', '.join(ready_prereqs)} in place")

    target = profile.target_role or "your target role"
    return f"Recommended because {' and '.join(reasons)}, and {skill_name} is required for {target}."


def to_out(c: ScoredCandidate) -> RecommendationOut:
    return RecommendationOut(
        ref_type=c.ref_type,
        ref_id=c.ref_id,
        title=c.title,
        skill_key=c.skill_key,
        score=c.score,
        score_breakdown=c.breakdown,
        why=c.why,
        difficulty=c.difficulty,
        estimated_minutes=c.estimated_minutes,
        url=c.url,
    )
