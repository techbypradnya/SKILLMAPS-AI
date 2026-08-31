from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models as m
from app.schemas.schemas import LearningPathOut, PathGenerateRequest, PathReplanRequest
from app.services.path_optimizer import generate_path, get_active_path_out, replan_path

router = APIRouter(prefix="/api/path", tags=["learning-path"])


def _get_profile(db: Session, profile_id: str) -> m.LearnerProfile:
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/generate", response_model=LearningPathOut)
def path_generate(payload: PathGenerateRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    if not profile.target_role:
        raise HTTPException(status_code=400, detail="Profile has no target_role yet; generate a skill graph first.")
    generate_path(db, profile)
    out = get_active_path_out(db, profile.id)
    return out


@router.get("", response_model=LearningPathOut)
def path_get(profile_id: str, db: Session = Depends(get_db)):
    out = get_active_path_out(db, profile_id)
    if not out:
        raise HTTPException(status_code=404, detail="No active learning path. Generate one first.")
    return out


@router.post("/replan", response_model=LearningPathOut)
def path_replan(payload: PathReplanRequest, db: Session = Depends(get_db)):
    profile = _get_profile(db, payload.profile_id)
    return replan_path(db, profile, reason=payload.reason)
