from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------- Profile / Goal ----------

class GoalAnalyzeRequest(BaseModel):
    text: str = Field(..., description="Free-text learner goal, e.g. 'I want to become an AI engineer...'")


class ExtractedProfile(BaseModel):
    goal: str
    target_role: str
    current_skills: list[str] = []
    experience_level: str = "beginner"
    timeline_weeks: int = 24
    weekly_hours: float = 8.0
    interests: list[str] = []
    learning_preferences: list[str] = []
    constraints: list[str] = []
    confidence: float = Field(0.6, description="AI confidence in this extraction, 0-1")
    source: str = Field("llm", description="'llm' or 'fallback_rules'")


class OnboardingAnswer(BaseModel):
    question: str
    answer: Optional[str] = None
    skipped: bool = False


class OnboardingSubmitRequest(BaseModel):
    profile_id: str
    answers: list[OnboardingAnswer]


class ProfileUpdateRequest(BaseModel):
    target_role: Optional[str] = None
    experience_level: Optional[str] = None
    timeline_weeks: Optional[int] = None
    weekly_hours: Optional[float] = None
    interests: Optional[list[str]] = None
    learning_preferences: Optional[list[str]] = None
    constraints: Optional[list[str]] = None
    current_skills: Optional[list[str]] = None


# ---------- Skill graph ----------

class SkillGraphGenerateRequest(BaseModel):
    profile_id: str
    target_role: str


class SkillNodeOut(BaseModel):
    id: str
    key: str
    name: str
    category: Optional[str] = None
    confidence: float = 0.0
    status: str = "unknown"
    evidence: list[dict[str, Any]] = []
    is_target: bool = True


class SkillEdgeOut(BaseModel):
    source: str
    target: str
    relation_type: str


class SkillGraphOut(BaseModel):
    nodes: list[SkillNodeOut]
    edges: list[SkillEdgeOut]


# ---------- Gap analysis ----------

class SkillGapItem(BaseModel):
    skill_key: str
    skill_name: str
    category: Optional[str]
    confidence: float
    status: str
    gap_score: float
    blocked_by: list[str] = []
    priority_rank: Optional[int] = None


class GapAnalysisOut(BaseModel):
    mastered: list[SkillGapItem]
    partial: list[SkillGapItem]
    missing: list[SkillGapItem]
    highest_impact_gaps: list[SkillGapItem]


# ---------- Recommendations ----------

class RecommendationOut(BaseModel):
    ref_type: str
    ref_id: str
    title: str
    skill_key: Optional[str]
    score: float
    score_breakdown: dict[str, float]
    why: str
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    url: Optional[str] = None


# ---------- Learning path ----------

class PathItemOut(BaseModel):
    id: str
    phase_index: int
    phase_title: str
    item_type: str
    ref_id: Optional[str]
    title: str
    estimated_minutes: int
    order_index: int
    status: str
    why: Optional[str]
    skill_key: Optional[str] = None


class LearningPathOut(BaseModel):
    id: str
    version: int
    target_role: Optional[str]
    items: list[PathItemOut]
    replanning_log: list[dict[str, Any]] = []


class PathGenerateRequest(BaseModel):
    profile_id: str


class PathReplanRequest(BaseModel):
    profile_id: str
    reason: Optional[str] = None


# ---------- Assessments ----------

class AssessmentGenerateRequest(BaseModel):
    profile_id: str
    skill_key: str


class AssessmentQuestionOut(BaseModel):
    id: str
    prompt: str
    options: list[str]
    difficulty: str
    order_index: int


class AssessmentOut(BaseModel):
    id: str
    skill_key: str
    title: str
    questions: list[AssessmentQuestionOut]


class AssessmentSubmitRequest(BaseModel):
    profile_id: str
    assessment_id: str
    answers: list[dict[str, Any]]  # [{question_id, chosen_index}]


class AssessmentResultOut(BaseModel):
    score_pct: float
    correct: int
    total: int
    weak_concepts: list[str]
    updated_confidence: float
    updated_status: str


# ---------- Feedback ----------

class FeedbackRequest(BaseModel):
    profile_id: str
    learning_path_item_id: Optional[str] = None
    rating: str
    confidence_1_5: Optional[int] = None


# ---------- What-if ----------

class WhatIfRequest(BaseModel):
    profile_id: str
    scenario: str  # free text, e.g. "skip SQL" or "1 hour/day"


class WhatIfOut(BaseModel):
    scenario: str
    interpreted_action: dict[str, Any]
    impact_summary: list[str]
    recalculated: bool
    time_saved_minutes: Optional[int] = None


# ---------- Chat companion ----------

class ChatRequest(BaseModel):
    profile_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    used_context: list[str] = []


# ---------- Dashboard ----------

class CareerReadinessOut(BaseModel):
    overall: float
    breakdown: dict[str, float]
    blockers: list[str]
    fastest_improvement: Optional[str]


class DashboardOut(BaseModel):
    profile_id: str
    target_role: Optional[str]
    overall_progress: float
    current_phase: Optional[str]
    learning_velocity: float
    career_readiness: CareerReadinessOut
    next_best_action: Optional[RecommendationOut]
    today_mission: list[PathItemOut]
    skill_summary: dict[str, int]  # counts by status


# ---------- Authentication ----------

class SignUpRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(...)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    full_name: Optional[str]
    created_at: str


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
