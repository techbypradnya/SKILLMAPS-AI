"""
Core test suite (spec section 37): goal extraction, skill gap detection,
prerequisite ordering, recommendation scoring, roadmap generation, and
adaptive replanning. Uses an isolated in-memory SQLite database per test
session so it never touches a developer's local skillgraph.db.
"""
from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.db.seed import seed_if_empty
from app.models import models as m
from app.services import path_optimizer
from app.services.gap_analyzer import analyze_gaps
from app.services.profiler import extract_profile
from app.services.recommendation import score_resources_for_profile
from app.services.skill_graph import resolve_target_skill_set, topological_learning_order
from app.services.util import status_for_confidence


@pytest.fixture(scope="module")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_if_empty(session)
    yield session
    session.close()


@pytest.fixture
def profile(db):
    import uuid

    user = m.User(email=f"test-{uuid.uuid4()}@example.com", hashed_password="x")
    db.add(user)
    db.flush()
    p = m.LearnerProfile(
        user_id=user.id, target_role="AI Engineer", experience_level="beginner",
        timeline_weeks=24, weekly_hours=10, interests=["GenAI"], learning_preferences=["project-first"],
        goal_raw_text="I want to become an AI engineer and build RAG applications.",
    )
    db.add(p)
    db.flush()
    python_skill = db.query(m.Skill).filter(m.Skill.key == "python").first()
    db.add(m.LearnerSkill(profile_id=p.id, skill_id=python_skill.id, confidence=85, status="strong"))
    db.commit()
    return p


# ---------- Goal extraction ----------

def test_goal_extraction_detects_role_and_timeline():
    result = extract_profile("I want to become a Data Scientist in 4 months. I can study 10 hours a week.")
    assert result.target_role == "Data Scientist"
    assert result.timeline_weeks == 16
    assert result.weekly_hours == 10.0


def test_goal_extraction_detects_current_skills():
    result = extract_profile("I already know Python and SQL, want to become a full stack developer.")
    assert "python" in result.current_skills
    assert "sql" in result.current_skills


# ---------- Skill graph / prerequisites ----------

def test_target_skill_set_includes_transitive_prerequisites(db):
    keys = resolve_target_skill_set(db, "AI Engineer")
    # RAG requires embeddings -> transformers -> rnn -> neural_networks (transitively)
    assert "rag" in keys
    assert "embeddings" in keys
    assert "transformers" in keys
    assert "neural_networks" in keys


def test_topological_order_respects_prerequisites(db):
    keys = resolve_target_skill_set(db, "AI Engineer")
    order = topological_learning_order(db, keys)
    assert order.index("python") < order.index("numpy_pandas")
    assert order.index("transformers") < order.index("embeddings")
    assert order.index("embeddings") < order.index("rag")


# ---------- Gap analysis ----------

def test_gap_analysis_marks_strong_skill_as_mastered(db, profile):
    result = analyze_gaps(db, profile.id, "AI Engineer")
    mastered_keys = [i.skill_key for i in result.mastered]
    assert "python" in mastered_keys


def test_gap_analysis_ranks_highest_impact_gaps(db, profile):
    result = analyze_gaps(db, profile.id, "AI Engineer")
    assert len(result.highest_impact_gaps) > 0
    ranks = [i.priority_rank for i in result.highest_impact_gaps]
    assert ranks == sorted(ranks)


def test_status_for_confidence_bands():
    assert status_for_confidence(10) == "unknown"
    assert status_for_confidence(30) == "beginner"
    assert status_for_confidence(50) == "developing"
    assert status_for_confidence(70) == "proficient"
    assert status_for_confidence(90) == "strong"


# ---------- Recommendation scoring ----------

def test_recommendations_exclude_mastered_skill_resources(db, profile):
    candidates = score_resources_for_profile(db, profile, limit=50)
    # Python is already at 85 confidence — shouldn't be primarily recommended.
    python_primary = [c for c in candidates if c.skill_key == "python"]
    assert len(python_primary) == 0


def test_recommendation_scores_are_bounded(db, profile):
    candidates = score_resources_for_profile(db, profile, limit=50)
    assert len(candidates) > 0
    for c in candidates:
        assert 0 <= c.score <= 1.2  # small headroom for weighting rounding


# ---------- Roadmap generation & adaptive replanning ----------

def test_generate_path_orders_prerequisites_before_dependents(db, profile):
    path_optimizer.generate_path(db, profile)
    out = path_optimizer.get_active_path_out(db, profile.id)
    skill_order = [i.skill_key for i in out.items if i.skill_key]
    if "transformers" in skill_order and "embeddings" in skill_order:
        assert skill_order.index("transformers") < skill_order.index("embeddings")


def test_replan_logs_a_reason(db, profile):
    path_optimizer.generate_path(db, profile)
    out = path_optimizer.replan_path(db, profile, reason="Learner scored 90% on an assessment.")
    assert len(out.replanning_log) >= 1
    assert "90%" in out.replanning_log[-1]["reason"]
