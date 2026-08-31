from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models as m
from app.schemas.schemas import (
    AssessmentGenerateRequest,
    AssessmentOut,
    AssessmentResultOut,
    AssessmentSubmitRequest,
    ChatRequest,
    ChatResponse,
    DashboardOut,
    FeedbackRequest,
    RecommendationOut,
    WhatIfOut,
    WhatIfRequest,
)
from app.services.assessment import generate_assessment, submit_assessment
from app.services.companion import chat as companion_chat
from app.services.dashboard import build_dashboard
from app.services.explanation import decision_trace, explain_journey
from app.services.feedback import record_feedback
from app.services.path_optimizer import replan_path
from app.services.recommendation import score_resources_for_profile, to_out
from app.services.what_if import simulate

router = APIRouter(prefix="/api", tags=["misc"])


def _get_profile(db: Session, profile_id: str) -> m.LearnerProfile:
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/recommendations", response_model=list[RecommendationOut])
def get_recommendations(profile_id: str, limit: int = 10, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    candidates = score_resources_for_profile(db, profile, limit=limit)
    results = []
    for c in candidates:
        out = to_out(c)
        results.append(out)
    return results


@router.get("/recommendations/{ref_id}/decision-trace")
def get_decision_trace(ref_id: str, profile_id: str, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    candidates = score_resources_for_profile(db, profile, limit=200)
    match = next((c for c in candidates if c.ref_id == ref_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"factors": decision_trace(match.breakdown)}


@router.post("/assessment/generate", response_model=AssessmentOut)
def assessment_generate(payload: AssessmentGenerateRequest, db: Session = Depends(get_db)):
    _get_profile(db, payload.profile_id)
    return generate_assessment(db, payload.profile_id, payload.skill_key)


@router.post("/assessment/submit", response_model=AssessmentResultOut)
def assessment_submit(payload: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    _get_profile(db, payload.profile_id)
    result = submit_assessment(db, payload.profile_id, payload.assessment_id, payload.answers)
    return result


@router.post("/assessment/submit-and-replan", response_model=AssessmentResultOut)
def assessment_submit_and_replan(payload: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    result = submit_assessment(db, payload.profile_id, payload.assessment_id, payload.answers)
    reason = (
        f"Assessment result of {result.score_pct}% updated skill confidence to {result.updated_confidence:.0f}/100."
    )
    replan_path(db, profile, reason=reason)
    return result


@router.post("/feedback")
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    record_feedback(db, profile, payload.learning_path_item_id, payload.rating, payload.confidence_1_5)
    return {"status": "recorded", "learning_velocity": profile.learning_velocity}


@router.post("/what-if", response_model=WhatIfOut)
def what_if(payload: WhatIfRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    return simulate(db, profile, payload.scenario)


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    return companion_chat(db, profile, payload.message)


@router.get("/journey/explain")
def journey_explain(profile_id: str, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    return {"explanation": explain_journey(db, profile)}


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(profile_id: str, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    return build_dashboard(db, profile)


@router.get("/projects")
def list_projects(profile_id: str, db: Session = Depends(get_db)):
    from app.services.skill_graph import learner_skill_map, resolve_target_skill_set

    profile = _get_profile(db, profile_id)
    target_keys = set(resolve_target_skill_set(db, profile.target_role or "AI Engineer"))
    learner_skills = learner_skill_map(db, profile.id)

    projects = db.query(m.Project).all()
    project_skill_rows = db.query(m.ProjectSkill).all()
    skills_by_id = {s.id: s for s in db.query(m.Skill).all()}
    project_to_skills: dict[str, list[str]] = {}
    for ps in project_skill_rows:
        skill = skills_by_id.get(ps.skill_id)
        if skill:
            project_to_skills.setdefault(ps.project_id, []).append(skill.key)

    out = []
    for p in projects:
        skill_keys = project_to_skills.get(p.id, [])
        relevant = [k for k in skill_keys if k in target_keys]
        if not relevant:
            continue
        confs = [(learner_skills.get(k).confidence if learner_skills.get(k) else 0.0) for k in relevant]
        readiness = round(sum(confs) / len(confs), 1) if confs else 0.0
        out.append(
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "difficulty": p.difficulty,
                "estimated_hours": p.estimated_hours,
                "portfolio_value": p.portfolio_value,
                "skills": relevant,
                "readiness_pct": readiness,
            }
        )
    out.sort(key=lambda x: -x["readiness_pct"])
    return out
