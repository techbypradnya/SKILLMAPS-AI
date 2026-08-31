from __future__ import annotations

from sqlalchemy.orm import Session

from app.data.seed_data import ASSESSMENT_BANK, PROJECTS, RESOURCES, SKILLS, SKILL_REQUIRES
from app.models import models as m


def seed_if_empty(db: Session) -> None:
    if db.query(m.Skill).first() is not None:
        return  # already seeded

    key_to_skill: dict[str, m.Skill] = {}
    for key, info in SKILLS.items():
        skill = m.Skill(key=key, name=info["name"], category=info["category"], description=info["description"])
        db.add(skill)
        key_to_skill[key] = skill
    db.flush()

    for from_key, to_key in SKILL_REQUIRES:
        db.add(
            m.SkillRelationship(
                from_skill_id=key_to_skill[from_key].id,
                to_skill_id=key_to_skill[to_key].id,
                relation_type="REQUIRES",
            )
        )

    for r in RESOURCES:
        resource = m.Resource(
            title=r["title"],
            provider=r.get("provider"),
            url=r.get("url"),
            resource_type=r.get("type", "course"),
            difficulty=r.get("difficulty", "beginner"),
            estimated_minutes=r.get("minutes", 60),
            quality_score=r.get("quality", 0.7),
            has_project=r.get("has_project", False),
        )
        db.add(resource)
        db.flush()
        for skill_key in r["skills"]:
            db.add(m.ResourceSkill(resource_id=resource.id, skill_id=key_to_skill[skill_key].id))

    for p in PROJECTS:
        project = m.Project(
            title=p["title"],
            description=p.get("description"),
            difficulty=p.get("difficulty", "beginner"),
            estimated_hours=p.get("hours", 4),
            portfolio_value=p.get("portfolio_value", "medium"),
        )
        db.add(project)
        db.flush()
        for skill_key in p["skills"]:
            db.add(m.ProjectSkill(project_id=project.id, skill_id=key_to_skill[skill_key].id))

    db.commit()


DEMO_PRESETS: dict[str, dict] = {
    "AI Engineer": {
        "email": "demo@skillgraph.ai",
        "name": "Alex",
        "goal": "I want to become an AI Engineer in 6 months. I know Python and basic ML. I can study 2 hours a day.",
        "experience_level": "intermediate",
        "timeline_weeks": 26,
        "weekly_hours": 14,
        "interests": ["GenAI", "LLM applications"],
        "learning_preferences": ["project-first", "video"],
        "skills": {
            "python": 82, "oop": 70, "data_structures": 55, "sql": 60,
            "numpy_pandas": 58, "probability": 40, "statistics": 38,
            "ml_regression": 35, "ml_classification": 28, "model_evaluation": 20,
            "neural_networks": 15,
        },
    },
    "Data Scientist": {
        "email": "demo-ds@skillgraph.ai",
        "name": "Priya",
        "goal": "I want to become a Data Scientist within 4 months. I know SQL and some statistics from my degree.",
        "experience_level": "beginner",
        "timeline_weeks": 18,
        "weekly_hours": 10,
        "interests": ["Analytics", "Business insights"],
        "learning_preferences": ["reading", "project-first"],
        "skills": {"sql": 65, "statistics": 45, "probability": 40, "python": 30, "numpy_pandas": 25},
    },
    "Full Stack Developer": {
        "email": "demo-fs@skillgraph.ai",
        "name": "Marcus",
        "goal": "I want to become a Full Stack Developer in 5 months. I know HTML/CSS and a bit of JavaScript.",
        "experience_level": "beginner",
        "timeline_weeks": 20,
        "weekly_hours": 12,
        "interests": ["Web apps", "Startups"],
        "learning_preferences": ["project-first", "video"],
        "skills": {"html_css": 70, "javascript": 45, "git": 40},
    },
    "Cybersecurity Analyst": {
        "email": "demo-sec@skillgraph.ai",
        "name": "Jordan",
        "goal": "I want to become a Cybersecurity Analyst in 6 months. I have general IT support experience.",
        "experience_level": "beginner",
        "timeline_weeks": 24,
        "weekly_hours": 10,
        "interests": ["Blue team", "Incident response"],
        "learning_preferences": ["reading", "video"],
        "skills": {"networking_fundamentals": 55, "os_fundamentals": 50, "security_fundamentals": 30},
    },
}


def seed_demo_learner(db: Session, role: str = "AI Engineer") -> m.User:
    """Create (or fetch) a preloaded demo learner for the given target role
    (spec sections 33, 49)."""
    preset = DEMO_PRESETS.get(role, DEMO_PRESETS["AI Engineer"])
    existing = db.query(m.User).filter(m.User.email == preset["email"]).first()
    if existing:
        return existing

    user = m.User(email=preset["email"], hashed_password="demo", display_name=preset["name"], is_demo=True)
    db.add(user)
    db.flush()

    profile = m.LearnerProfile(
        user_id=user.id,
        goal_raw_text=preset["goal"],
        target_role=role,
        experience_level=preset["experience_level"],
        timeline_weeks=preset["timeline_weeks"],
        weekly_hours=preset["weekly_hours"],
        interests=preset["interests"],
        learning_preferences=preset["learning_preferences"],
        constraints=[],
    )
    db.add(profile)
    db.flush()

    for key, conf in preset["skills"].items():
        skill = db.query(m.Skill).filter(m.Skill.key == key).first()
        if not skill:
            continue
        db.add(
            m.LearnerSkill(
                profile_id=profile.id,
                skill_id=skill.id,
                confidence=conf,
                status=_status_for_confidence(conf),
                evidence=[{"source": "onboarding_self_report", "detail": "Learner self-reported during diagnostic", "points": conf}],
            )
        )
    db.commit()
    return user


def _status_for_confidence(conf: float) -> str:
    if conf < 20:
        return "unknown"
    if conf < 40:
        return "beginner"
    if conf < 60:
        return "developing"
    if conf < 80:
        return "proficient"
    return "strong"
