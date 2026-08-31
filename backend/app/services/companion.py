"""
AI Learning Companion (spec section 19).

The companion always has access to the learner's real profile, skill gaps,
and active roadmap — answers are grounded in that context. With an LLM
configured, the context is passed as a system prompt so responses stay
on-topic and factual about the learner's own data. Without one, a small set
of intent-matching rules covers the example prompts from the spec so the
feature still works end-to-end in Demo Intelligence Mode.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import models as m
from app.schemas.schemas import ChatResponse
from app.services.gap_analyzer import analyze_gaps
from app.services.llm_provider import get_llm_provider
from app.services.path_optimizer import get_active_path_out


def _context_summary(db: Session, profile: m.LearnerProfile) -> tuple[str, list[str]]:
    gaps = analyze_gaps(db, profile.id, profile.target_role or "AI Engineer")
    path_out = get_active_path_out(db, profile.id)
    next_item = next((i for i in (path_out.items if path_out else []) if i.status == "pending"), None)

    used_context = ["learner_profile", "skill_gap_analysis"]
    lines = [
        f"Target role: {profile.target_role}",
        f"Weekly hours available: {profile.weekly_hours}",
        f"Mastered skills: {', '.join(i.skill_name for i in gaps.mastered) or 'none yet'}",
        f"Biggest gaps (highest impact first): {', '.join(i.skill_name for i in gaps.highest_impact_gaps) or 'none'}",
    ]
    if next_item:
        lines.append(f"Next roadmap item: {next_item.title} ({next_item.estimated_minutes} min) — {next_item.why}")
        used_context.append("active_learning_path")
    return "\n".join(lines), used_context


def _rule_based_reply(message: str, db: Session, profile: m.LearnerProfile, context: str) -> str:
    msg = message.lower()
    gaps = analyze_gaps(db, profile.id, profile.target_role or "AI Engineer")

    if "biggest weakness" in msg or "weakest" in msg:
        if gaps.highest_impact_gaps:
            top = gaps.highest_impact_gaps[0]
            return (
                f"Right now your highest-impact gap is **{top.skill_name}** — you're at an "
                f"AI-estimated {top.confidence:.0f}/100. Closing it unblocks the most downstream skills "
                f"in your roadmap toward {profile.target_role}."
            )
        return "You don't have any major tracked gaps yet — try running the diagnostic or generating your skill graph first."

    if "today" in msg or "what should i do" in msg:
        path_out = get_active_path_out(db, profile.id)
        next_item = next((i for i in (path_out.items if path_out else []) if i.status == "pending"), None)
        if next_item:
            return f"Your next best action is: **{next_item.title}** ({next_item.estimated_minutes} min). {next_item.why}"
        return "You don't have an active roadmap yet — generate one from your profile first."

    if "skip" in msg and "course" in msg:
        return "It depends on the evidence: if you already have assessment or project evidence for that skill, I can mark it mastered and remove the resource from your roadmap — try the What-If simulator to see the exact impact."

    if "quiz me" in msg or "quiz" in msg:
        return "Head to the Assessment page and pick a skill — I'll generate an adaptive quiz that starts easy and escalates in difficulty based on how you're doing."

    if "why" in msg and "linear algebra" in msg:
        return "Linear algebra underpins how neural networks represent and transform data (vectors, matrices, gradients) — it's a direct prerequisite for the Deep Learning skills on your path."

    if "simpler" in msg or "don't understand" in msg or "explain" in msg:
        return (
            "Happy to simplify. Tell me which specific concept is unclear and I'll break it into a plain-language "
            "explanation with a concrete example — the more specific you are, the better I can target it."
        )

    if "30 minutes" in msg or "only have" in msg:
        return "With 30 minutes, focus on your single highest-impact gap rather than starting something new — check today's mission on your dashboard for a right-sized task."

    if "change my goal" in msg:
        return "Yes — update your target role on the Profile page and I'll rebuild your skill graph, gap analysis, and roadmap around the new goal."

    return (
        "I can see your current profile and roadmap, but I don't have a specific rule for that question in "
        "demo mode. Try asking about your biggest weakness, what to do today, or a specific skill you want explained."
    )


def chat(db: Session, profile: m.LearnerProfile, message: str) -> ChatResponse:
    context, used_context = _context_summary(db, profile)

    llm = get_llm_provider()
    if llm.available:
        system = (
            "You are the AI Learning Companion inside SkillGraph AI, an adaptive learning platform. "
            "You have access to the learner's real profile and roadmap context below. Answer only using "
            "this context plus general knowledge of the subject matter — never invent specific facts about "
            "the learner that aren't in the context. Keep answers concise (3-5 sentences) and actionable.\n\n"
            f"LEARNER CONTEXT:\n{context}"
        )
        result = llm.complete_text(system, message, max_tokens=400)
        if result.ok:
            db.add(m.Conversation(profile_id=profile.id, role="user", content=message))
            db.add(m.Conversation(profile_id=profile.id, role="assistant", content=result.text))
            db.commit()
            return ChatResponse(reply=result.text, used_context=used_context)

    reply = _rule_based_reply(message, db, profile, context)
    db.add(m.Conversation(profile_id=profile.id, role="user", content=message))
    db.add(m.Conversation(profile_id=profile.id, role="assistant", content=reply))
    db.commit()
    return ChatResponse(reply=reply, used_context=used_context)
