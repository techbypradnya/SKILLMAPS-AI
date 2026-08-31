"""
Adaptive Assessment Engine (spec section 11) + Evidence-Based Mastery
(spec section 10).

Questions are drawn from the curated ASSESSMENT_BANK when available (highest
quality), ordered easy -> medium -> hard so an assessment naturally escalates
difficulty. For skills without a hand-authored bank, the LLM generates
questions grounded in the skill name/description; if the LLM is unavailable,
a deterministic templated fallback keeps the feature working end to end.

Submitting an assessment updates the learner's AI-estimated proficiency using
a transparent, additive evidence model (spec section 10) rather than a single
opaque "AI decided" number.
"""
from __future__ import annotations

import random

from sqlalchemy.orm import Session

from app.data.seed_data import ASSESSMENT_BANK
from app.models import models as m
from app.schemas.schemas import AssessmentOut, AssessmentQuestionOut, AssessmentResultOut
from app.services.llm_provider import get_llm_provider
from app.services.util import clamp, status_for_confidence

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def _generic_fallback_questions(skill_name: str) -> list[dict]:
    return [
        {
            "prompt": f"Which statement best describes {skill_name}?",
            "options": [
                f"{skill_name} is a core capability relevant to this learning path",
                f"{skill_name} is unrelated to software or data work",
                f"{skill_name} cannot be learned through practice",
                f"{skill_name} is only a marketing term",
            ],
            "correct_index": 0,
            "difficulty": "easy",
            "concept": "definition",
        },
        {
            "prompt": f"A learner who is 'developing' in {skill_name} most likely:",
            "options": [
                "Has no exposure to the topic at all",
                "Has some understanding but needs more guided practice",
                "Could teach an expert-level course on it",
                "Has already mastered every edge case",
            ],
            "correct_index": 1,
            "difficulty": "medium",
            "concept": "proficiency_bands",
        },
        {
            "prompt": f"What is the best way to build verifiable evidence of {skill_name} mastery?",
            "options": [
                "Only watching videos passively",
                "Completing practice problems and a real project",
                "Reading the topic's Wikipedia page once",
                "Guessing on a quiz",
            ],
            "correct_index": 1,
            "difficulty": "hard",
            "concept": "evidence",
        },
    ]


def _llm_generated_questions(skill_name: str, skill_description: str) -> list[dict] | None:
    llm = get_llm_provider()
    if not llm.available:
        return None
    system = (
        "You write multiple-choice assessment questions for a learning "
        "platform. Respond with ONLY a JSON array (no prose), each item: "
        '{"prompt": string, "options": string[4], "correct_index": int, '
        '"difficulty": "easy"|"medium"|"hard", "concept": string}. '
        "Produce exactly 4 questions: 2 easy, 1 medium, 1 hard."
    )
    user = f"Skill: {skill_name}\nDescription: {skill_description}"
    result = llm.complete_json(system, user, max_tokens=700)
    if result.ok and isinstance(result.data, list) and len(result.data) >= 2:
        return result.data
    return None


def generate_assessment(db: Session, profile_id: str, skill_key: str) -> AssessmentOut:
    skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
    if not skill:
        raise ValueError(f"Unknown skill: {skill_key}")

    bank = ASSESSMENT_BANK.get(skill_key)
    source = "curated_bank"
    if not bank:
        bank = _llm_generated_questions(skill.name, skill.description or "")
        source = "llm_generated" if bank else "template_fallback"
        if not bank:
            bank = _generic_fallback_questions(skill.name)

    ordered = sorted(bank, key=lambda q: DIFFICULTY_ORDER.get(q.get("difficulty", "medium"), 1))

    assessment = m.Assessment(profile_id=profile_id, skill_id=skill.id, title=f"{skill.name} Adaptive Assessment")
    db.add(assessment)
    db.flush()

    q_out = []
    for i, q in enumerate(ordered):
        question = m.AssessmentQuestion(
            assessment_id=assessment.id,
            prompt=q["prompt"],
            options=q["options"],
            correct_option_index=q["correct_index"],
            difficulty=q.get("difficulty", "medium"),
            concept_tag=q.get("concept"),
            order_index=i,
        )
        db.add(question)
        db.flush()
        q_out.append(
            AssessmentQuestionOut(
                id=question.id, prompt=question.prompt, options=question.options,
                difficulty=question.difficulty, order_index=question.order_index,
            )
        )
    db.commit()

    return AssessmentOut(id=assessment.id, skill_key=skill_key, title=assessment.title, questions=q_out)


def submit_assessment(db: Session, profile_id: str, assessment_id: str, answers: list[dict]) -> AssessmentResultOut:
    assessment = db.query(m.Assessment).filter(m.Assessment.id == assessment_id).first()
    if not assessment:
        raise ValueError("Assessment not found")
    questions = (
        db.query(m.AssessmentQuestion)
        .filter(m.AssessmentQuestion.assessment_id == assessment_id)
        .order_by(m.AssessmentQuestion.order_index)
        .all()
    )
    q_by_id = {q.id: q for q in questions}

    graded = []
    weak_concepts = []
    correct_count = 0
    for ans in answers:
        q = q_by_id.get(ans.get("question_id"))
        if not q:
            continue
        is_correct = int(ans.get("chosen_index", -1)) == q.correct_option_index
        if is_correct:
            correct_count += 1
        else:
            if q.concept_tag:
                weak_concepts.append(q.concept_tag)
        graded.append({"question_id": q.id, "chosen_index": ans.get("chosen_index"), "correct": is_correct, "difficulty": q.difficulty})

    total = len(questions)
    score_pct = round(100 * correct_count / total, 1) if total else 0.0

    attempt = m.AssessmentAttempt(
        assessment_id=assessment_id, profile_id=profile_id, answers=graded,
        score_pct=score_pct, weak_concepts=list(dict.fromkeys(weak_concepts)),
    )
    db.add(attempt)

    # --- Evidence-based mastery update (spec section 10) ---
    learner_skill = (
        db.query(m.LearnerSkill)
        .filter(m.LearnerSkill.profile_id == profile_id, m.LearnerSkill.skill_id == assessment.skill_id)
        .first()
    )
    if not learner_skill:
        learner_skill = m.LearnerSkill(profile_id=profile_id, skill_id=assessment.skill_id, confidence=0.0, status="unknown", evidence=[])
        db.add(learner_skill)
        db.flush()

    # Weighted by difficulty: hard questions count more toward proficiency.
    difficulty_points = {"easy": 8, "medium": 12, "hard": 18}
    earned = sum(difficulty_points.get(a["difficulty"], 10) for a in graded if a["correct"])
    possible = sum(difficulty_points.get(a["difficulty"], 10) for a in graded)
    assessment_component = (earned / possible * 30) if possible else 0  # up to +30 pts

    new_confidence = clamp(learner_skill.confidence * 0.6 + (learner_skill.confidence + assessment_component) * 0.4)
    # Blend: keep some prior evidence, but let this fresh assessment meaningfully move the needle.
    new_confidence = clamp((learner_skill.confidence + assessment_component))

    evidence = list(learner_skill.evidence or [])
    evidence.append(
        {
            "source": "assessment",
            "detail": f"Scored {score_pct}% on {assessment.title}",
            "points": round(assessment_component, 1),
        }
    )
    learner_skill.confidence = new_confidence
    learner_skill.status = status_for_confidence(new_confidence)
    learner_skill.evidence = evidence

    db.commit()

    return AssessmentResultOut(
        score_pct=score_pct,
        correct=correct_count,
        total=total,
        weak_concepts=attempt.weak_concepts,
        updated_confidence=round(learner_skill.confidence, 1),
        updated_status=learner_skill.status,
    )
