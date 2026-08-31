from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.seed_data import ROLE_SKILLS
from app.db.session import get_db
from app.models import models as m
from app.schemas.schemas import (
    ExtractedProfile,
    GoalAnalyzeRequest,
    OnboardingSubmitRequest,
    ProfileUpdateRequest,
)
from app.services.profiler import extract_profile
from app.services.util import status_for_confidence

router = APIRouter(prefix="/api", tags=["profile"])

ONBOARDING_QUESTIONS = [
    "What is your ultimate learning or career goal?",
    "What do you already know?",
    "What have you studied or built previously?",
    "How much time can you dedicate per week?",
    "What is your target deadline?",
    "Which learning format do you prefer (video, reading, hands-on projects)?",
    "How do you prefer to learn — theory-first or project-first?",
    "What projects have you already built, if any?",
]


@router.get("/onboarding/questions")
def get_onboarding_questions():
    return {"questions": ONBOARDING_QUESTIONS}


@router.post("/goals/analyze", response_model=ExtractedProfile)
@router.post("/profile/analyze", response_model=ExtractedProfile)
def analyze_goal(payload: GoalAnalyzeRequest):
    return extract_profile(payload.text)


def _get_or_create_demo_user(db: Session) -> m.User:
    user = db.query(m.User).filter(m.User.email == "guest@skillgraph.ai").first()
    if user:
        return user
    user = m.User(email="guest@skillgraph.ai", hashed_password="guest")
    db.add(user)
    db.flush()
    return user


@router.post("/profile/create-from-text")
def create_profile_from_text(payload: GoalAnalyzeRequest, db: Session = Depends(get_db)):
    """Convenience endpoint: extract profile from free text AND persist it,
    returning the new profile_id for subsequent calls."""
    extracted = extract_profile(payload.text)
    user = _get_or_create_demo_user(db)

    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.user_id == user.id).first()
    if not profile:
        profile = m.LearnerProfile(user_id=user.id)
        db.add(profile)

    profile.goal_raw_text = extracted.goal
    profile.target_role = extracted.target_role
    profile.experience_level = extracted.experience_level
    profile.timeline_weeks = extracted.timeline_weeks
    profile.weekly_hours = extracted.weekly_hours
    profile.interests = extracted.interests
    profile.learning_preferences = extracted.learning_preferences
    profile.constraints = extracted.constraints
    db.commit()
    db.flush()

    for skill_key in extracted.current_skills:
        skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
        if not skill:
            continue
        existing = (
            db.query(m.LearnerSkill)
            .filter(m.LearnerSkill.profile_id == profile.id, m.LearnerSkill.skill_id == skill.id)
            .first()
        )
        if not existing:
            db.add(
                m.LearnerSkill(
                    profile_id=profile.id, skill_id=skill.id, confidence=45.0,
                    status=status_for_confidence(45.0),
                    evidence=[{"source": "self_report", "detail": "Mentioned in goal description", "points": 45}],
                )
            )
    db.commit()

    return {"profile_id": profile.id, "extracted": extracted}


@router.get("/profile/{profile_id}")
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": profile.id,
        "goal_raw_text": profile.goal_raw_text,
        "target_role": profile.target_role,
        "experience_level": profile.experience_level,
        "timeline_weeks": profile.timeline_weeks,
        "weekly_hours": profile.weekly_hours,
        "interests": profile.interests,
        "learning_preferences": profile.learning_preferences,
        "constraints": profile.constraints,
        "learning_velocity": profile.learning_velocity,
        "available_roles": list(ROLE_SKILLS.keys()),
    }


@router.patch("/profile/{profile_id}")
def update_profile(profile_id: str, payload: ProfileUpdateRequest, db: Session = Depends(get_db)):
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field in ["target_role", "experience_level", "timeline_weeks", "weekly_hours", "interests", "learning_preferences", "constraints"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(profile, field, value)

    if payload.current_skills is not None:
        for skill_key in payload.current_skills:
            skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
            if not skill:
                continue
            existing = (
                db.query(m.LearnerSkill)
                .filter(m.LearnerSkill.profile_id == profile.id, m.LearnerSkill.skill_id == skill.id)
                .first()
            )
            if not existing:
                db.add(m.LearnerSkill(profile_id=profile.id, skill_id=skill.id, confidence=40.0, status=status_for_confidence(40.0)))

    db.commit()
    return {"status": "updated"}


@router.post("/onboarding/submit")
def submit_onboarding(payload: OnboardingSubmitRequest, db: Session = Depends(get_db)):
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == payload.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.onboarding_answers = {a.question: (a.answer if not a.skipped else None) for a in payload.answers}
    db.commit()
    return {"status": "saved"}
