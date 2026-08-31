"""
Counterfactual Learning Insight / "What If?" Simulator (spec section 17).

Parses a small set of supported scenario shapes (skip a skill, change daily/
weekly time budget) with simple rules, then actually recomputes against the
real skill graph and path optimizer rather than hand-waving a plausible-
sounding LLM answer — so the numbers shown are grounded in the same engine
that generates the real roadmap.
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.data.seed_data import SKILLS
from app.models import models as m
from app.schemas.schemas import WhatIfOut
from app.services.path_optimizer import estimate_completion_weeks, get_active_path
from app.services.recommendation import score_resources_for_profile
from app.services.skill_graph import get_dependents, resolve_target_skill_set

SKIP_PATTERN = re.compile(r"skip\s+([a-zA-Z0-9\-\s]+)")
HOURS_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*hours?\s*(?:a|per|/)\s*(day|week)")


def _match_skill_key(text: str) -> str | None:
    text_lower = text.lower().strip()
    for key, info in SKILLS.items():
        if info["name"].lower() in text_lower or key.replace("_", " ") in text_lower:
            return key
    return None


def simulate(db: Session, profile: m.LearnerProfile, scenario: str) -> WhatIfOut:
    scenario_lower = scenario.lower()

    skip_match = SKIP_PATTERN.search(scenario_lower)
    hours_match = HOURS_PATTERN.search(scenario_lower)

    if skip_match:
        return _simulate_skip(db, profile, scenario, skip_match.group(1))
    if hours_match:
        return _simulate_time_change(db, profile, scenario, float(hours_match.group(1)), hours_match.group(2))

    return WhatIfOut(
        scenario=scenario,
        interpreted_action={"type": "unsupported"},
        impact_summary=[
            "I can currently simulate two kinds of what-if questions: skipping a specific skill "
            "(\"what if I skip SQL?\"), or changing your study time (\"what if I only have 1 hour a day?\"). "
            "Try rephrasing your scenario using one of those shapes.",
        ],
        recalculated=False,
    )


def _simulate_skip(db: Session, profile: m.LearnerProfile, scenario: str, raw_skill: str) -> WhatIfOut:
    skill_key = _match_skill_key(raw_skill)
    if not skill_key:
        return WhatIfOut(
            scenario=scenario,
            interpreted_action={"type": "skip", "skill": raw_skill.strip()},
            impact_summary=[f"I couldn't match '{raw_skill.strip()}' to a known skill in your roadmap."],
            recalculated=False,
        )

    target_keys = set(resolve_target_skill_set(db, profile.target_role or "AI Engineer"))
    dependents = [d for d in get_dependents(db, skill_key) if d in target_keys]
    skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()

    path = get_active_path(db, profile.id)
    time_saved = 0
    if path:
        items = db.query(m.LearningPathItem).filter(
            m.LearningPathItem.learning_path_id == path.id, m.LearningPathItem.skill_id == (skill.id if skill else None)
        ).all()
        time_saved = sum(i.estimated_minutes for i in items)

    impact = [f"Skipping {skill.name if skill else skill_key} saves approximately {time_saved} minutes in your current roadmap."]
    if dependents:
        dep_names = [db.query(m.Skill).filter(m.Skill.key == d).first().name for d in dependents[:4]]
        impact.append(
            f"It creates a prerequisite gap for: {', '.join(n for n in dep_names if n)}. "
            "Those skills would remain blocked until this is learned."
        )
    else:
        impact.append("No other target skills directly require it, so the downstream risk is low.")

    if skill_key in {"sql", "statistics", "probability"}:
        impact.append("A minimal, faster-to-learn subset could substitute for full mastery in the short term.")

    return WhatIfOut(
        scenario=scenario,
        interpreted_action={"type": "skip", "skill_key": skill_key},
        impact_summary=impact,
        recalculated=True,
        time_saved_minutes=time_saved,
    )


def _simulate_time_change(db: Session, profile: m.LearnerProfile, scenario: str, amount: float, unit: str) -> WhatIfOut:
    new_weekly_hours = amount * 7 if unit == "day" else amount
    old_weekly_hours = profile.weekly_hours or 8.0

    path = get_active_path(db, profile.id)
    total_minutes = 0
    if path:
        items = db.query(m.LearningPathItem).filter(m.LearningPathItem.learning_path_id == path.id).all()
        total_minutes = sum(i.estimated_minutes for i in items if i.status != "done")

    old_weeks = estimate_completion_weeks(total_minutes, old_weekly_hours)
    new_weeks = estimate_completion_weeks(total_minutes, new_weekly_hours)

    direction = "extend" if new_weeks > old_weeks else "shorten"
    impact = [
        f"At {new_weekly_hours:.1f} hours/week (vs your current {old_weekly_hours:.1f}), your remaining roadmap "
        f"would {direction} from an estimated {old_weeks} weeks to about {new_weeks} weeks.",
    ]
    if new_weekly_hours < old_weekly_hours:
        impact.append("The Time-Budget Optimizer would shift toward higher-leverage resources and trim optional practice to protect project time.")
    else:
        impact.append("The extra time would mostly go toward additional practice and an earlier start on your capstone project.")

    return WhatIfOut(
        scenario=scenario,
        interpreted_action={"type": "time_change", "new_weekly_hours": new_weekly_hours},
        impact_summary=impact,
        recalculated=True,
    )
