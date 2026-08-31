from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models as m
from app.schemas.schemas import GapAnalysisOut, SkillGraphGenerateRequest, SkillGraphOut
from app.services.gap_analyzer import analyze_gaps
from app.services.skill_graph import build_skill_graph_out

router = APIRouter(prefix="/api", tags=["skill-graph"])


def _get_profile(db: Session, profile_id: str) -> m.LearnerProfile:
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/skill-graph/generate", response_model=SkillGraphOut)
def generate_skill_graph(payload: SkillGraphGenerateRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    profile.target_role = payload.target_role
    db.commit()
    return build_skill_graph_out(db, payload.profile_id, payload.target_role)


@router.get("/skill-graph", response_model=SkillGraphOut)
def get_skill_graph(profile_id: str, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    return build_skill_graph_out(db, profile_id, profile.target_role or "AI Engineer")


@router.post("/gaps/analyze", response_model=GapAnalysisOut)
def gaps_analyze(payload: SkillGraphGenerateRequest, db: Session = Depends(get_db)):
    _get_profile(db, payload.profile_id)
    return analyze_gaps(db, payload.profile_id, payload.target_role)


@router.get("/gaps", response_model=GapAnalysisOut)
def gaps_get(profile_id: str, db: Session = Depends(get_db)):
    profile = _get_profile(db, profile_id)
    return analyze_gaps(db, profile_id, profile.target_role or "AI Engineer")
