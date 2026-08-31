from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.data.seed_data import ROLE_SKILLS
from app.db.seed import DEMO_PRESETS, seed_demo_learner
from app.db.session import get_db
from app.models import models as m
from app.services.llm_provider import get_llm_provider

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/roles")
def demo_roles():
    return {
        "roles": [
            {"role": role, "learner_name": DEMO_PRESETS[role]["name"], "goal": DEMO_PRESETS[role]["goal"]}
            for role in ROLE_SKILLS.keys()
        ]
    }


@router.post("/start")
def demo_start(role: str = "AI Engineer", db: Session = Depends(get_db)):
    user = seed_demo_learner(db, role=role)
    profile = db.query(m.LearnerProfile).filter(m.LearnerProfile.user_id == user.id).first()
    return {"profile_id": profile.id, "target_role": profile.target_role, "learner_name": user.display_name}


@router.get("/intelligence-mode")
def intelligence_mode():
    llm = get_llm_provider()
    return {"mode": "live_llm" if llm.available else "demo_intelligence", "provider": llm._provider_name}
