"""
Database models for SkillGraph AI.

Tables map directly onto the domain described in the product spec:
users, learner_profiles, skills, skill_relationships, learner_skills,
resources, resource_skills, projects, project_skills, assessments,
assessment_questions, assessment_attempts, learning_paths,
learning_path_items, progress, feedback, recommendations, conversations.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("LearnerProfile", back_populates="user", uselist=False)


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)

    goal_raw_text = Column(Text, nullable=True)
    target_role = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)  # beginner|intermediate|advanced
    timeline_weeks = Column(Integer, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    interests = Column(JSON, default=list)
    learning_preferences = Column(JSON, default=list)  # e.g. video, reading, project-first
    constraints = Column(JSON, default=list)

    learning_velocity = Column(Float, default=0.0)  # AI-derived product metric, 0-1 scale
    consistency_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)

    onboarding_answers = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=gen_id)
    key = Column(String, unique=True, nullable=False, index=True)  # stable slug e.g. "python"
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # e.g. Programming, Data, ML, GenAI, Production
    description = Column(Text, nullable=True)


class SkillRelationship(Base):
    """Directed edges between skills, e.g. REQUIRES / RELATED_TO / PART_OF."""

    __tablename__ = "skill_relationships"

    id = Column(String, primary_key=True, default=gen_id)
    from_skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    to_skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    relation_type = Column(String, nullable=False)  # REQUIRES, RELATED_TO, PART_OF
    weight = Column(Float, default=1.0)


class LearnerSkill(Base):
    """A learner's AI-estimated proficiency for a given skill, with evidence."""

    __tablename__ = "learner_skills"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)

    confidence = Column(Float, default=0.0)  # 0-100 "AI-estimated proficiency"
    evidence = Column(JSON, default=list)  # list of {source, detail, points, ts}
    status = Column(String, default="unknown")  # unknown|beginner|developing|proficient|strong
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    provider = Column(String, nullable=True)
    url = Column(String, nullable=True)
    resource_type = Column(String, default="course")  # course|video|article|doc|book|exercise
    difficulty = Column(String, default="beginner")  # beginner|intermediate|advanced
    estimated_minutes = Column(Integer, default=60)
    format = Column(String, default="self-paced")
    quality_score = Column(Float, default=0.7)  # 0-1 curated quality heuristic
    has_project = Column(Boolean, default=False)
    embedding = Column(JSON, nullable=True)  # cached vector, list[float]


class ResourceSkill(Base):
    __tablename__ = "resource_skills"

    id = Column(String, primary_key=True, default=gen_id)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    teaches_weight = Column(Float, default=1.0)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, default="beginner")
    estimated_hours = Column(Float, default=4.0)
    portfolio_value = Column(String, default="medium")  # low|medium|high


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    id = Column(String, primary_key=True, default=gen_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    demonstrates_weight = Column(Float, default=1.0)


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(String, primary_key=True, default=gen_id)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(JSON, default=list)
    correct_option_index = Column(Integer, nullable=False)
    difficulty = Column(String, default="easy")  # easy|medium|hard
    concept_tag = Column(String, nullable=True)
    order_index = Column(Integer, default=0)


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String, primary_key=True, default=gen_id)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    answers = Column(JSON, default=list)  # list of {question_id, chosen_index, correct}
    score_pct = Column(Float, default=0.0)
    weak_concepts = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    target_role = Column(String, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String, default="active")  # active|superseded
    replanning_log = Column(JSON, default=list)  # list of {reason, change, ts}
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(String, primary_key=True, default=gen_id)
    learning_path_id = Column(String, ForeignKey("learning_paths.id"), nullable=False)
    phase_index = Column(Integer, default=0)
    phase_title = Column(String, nullable=True)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=True)
    item_type = Column(String, default="resource")  # resource|project|assessment|checkpoint
    ref_id = Column(String, nullable=True)  # resource_id / project_id / assessment_id
    title = Column(String, nullable=False)
    estimated_minutes = Column(Integer, default=60)
    order_index = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending|in_progress|done|skipped
    why = Column(Text, nullable=True)  # explanation engine output
    score = Column(Float, default=0.0)  # recommendation score at generation time


class Progress(Base):
    __tablename__ = "progress"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    learning_path_item_id = Column(String, ForeignKey("learning_path_items.id"), nullable=True)
    event_type = Column(String, nullable=False)  # started|completed|skipped|scored
    detail = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    learning_path_item_id = Column(String, ForeignKey("learning_path_items.id"), nullable=True)
    rating = Column(String, nullable=False)  # too_easy|good|too_difficult|not_relevant|already_knew|need_more_practice
    confidence_1_5 = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    ref_type = Column(String, nullable=False)  # resource|project
    ref_id = Column(String, nullable=False)
    skill_id = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    score_breakdown = Column(JSON, default=dict)
    why = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_id)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    role = Column(String, nullable=False)  # user|assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
