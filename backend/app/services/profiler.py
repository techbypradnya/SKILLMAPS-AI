"""
Natural-language goal understanding (spec section 4).

Turns free text like:
  "I am a final-year computer engineering student. I know Python and basic
   ML. I want to become an AI engineer ... in 5 months. I can study 2 hours
   per day."
into a structured profile. Uses the LLM when available; otherwise falls back
to a deterministic keyword/regex extractor so the feature always works.
"""
from __future__ import annotations

import re

from app.data.seed_data import ROLE_SKILLS, SKILLS
from app.schemas.schemas import ExtractedProfile
from app.services.llm_provider import get_llm_provider

ROLE_ALIASES: dict[str, list[str]] = {
    "AI Engineer": ["ai engineer", "genai engineer", "generative ai engineer", "ml engineer", "machine learning engineer", "llm engineer"],
    "Data Scientist": ["data scientist", "data science"],
    "Full Stack Developer": ["full stack", "fullstack", "web developer", "software engineer", "frontend", "backend developer"],
    "Cybersecurity Analyst": ["cybersecurity", "security analyst", "infosec", "pentester", "penetration tester", "soc analyst"],
}

SKILL_MENTION_PATTERNS = {key: info["name"].lower() for key, info in SKILLS.items()}


def _detect_role(text_lower: str) -> str:
    for role, aliases in ROLE_ALIASES.items():
        if any(alias in text_lower for alias in aliases):
            return role
    return "AI Engineer"  # sensible default for this product's core narrative


def _detect_timeline_weeks(text_lower: str) -> int:
    m = re.search(r"(\d+)\s*month", text_lower)
    if m:
        return int(m.group(1)) * 4
    m = re.search(r"(\d+)\s*week", text_lower)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*year", text_lower)
    if m:
        return int(m.group(1)) * 52
    return 24  # default ~6 months


def _detect_weekly_hours(text_lower: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*hours?\s*(?:a|per|/)\s*day", text_lower)
    if m:
        return round(float(m.group(1)) * 7, 1)
    m = re.search(r"(\d+(?:\.\d+)?)\s*hours?\s*(?:a|per|/)\s*week", text_lower)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*hrs?\s*(?:a|per|/)\s*day", text_lower)
    if m:
        return round(float(m.group(1)) * 7, 1)
    return 8.0


def _detect_experience(text_lower: str) -> str:
    if any(w in text_lower for w in ["beginner", "new to", "just starting", "no experience", "never coded"]):
        return "beginner"
    if any(w in text_lower for w in ["advanced", "expert", "senior", "years of experience"]):
        return "advanced"
    return "intermediate" if any(w in text_lower for w in ["know", "familiar", "some experience", "basic"]) else "beginner"


def _detect_current_skills(text_lower: str) -> list[str]:
    found = []
    for key, name_lower in SKILL_MENTION_PATTERNS.items():
        if name_lower in text_lower or key.replace("_", " ") in text_lower:
            found.append(key)
    # common shorthand
    if "ml" in re.findall(r"\bml\b", text_lower):
        found.append("ml_classification") if "ml_classification" not in found else None
    return list(dict.fromkeys(found))


def _detect_preferences(text_lower: str) -> list[str]:
    prefs = []
    if "project" in text_lower or "hands-on" in text_lower or "hands on" in text_lower:
        prefs.append("project-first")
    if "video" in text_lower:
        prefs.append("video")
    if "read" in text_lower or "book" in text_lower or "article" in text_lower:
        prefs.append("reading")
    return prefs or ["project-first"]


def _rule_based_extract(text: str) -> ExtractedProfile:
    text_lower = text.lower()
    role = _detect_role(text_lower)
    return ExtractedProfile(
        goal=text.strip(),
        target_role=role,
        current_skills=_detect_current_skills(text_lower),
        experience_level=_detect_experience(text_lower),
        timeline_weeks=_detect_timeline_weeks(text_lower),
        weekly_hours=_detect_weekly_hours(text_lower),
        interests=[],
        learning_preferences=_detect_preferences(text_lower),
        constraints=[],
        confidence=0.55,
        source="fallback_rules",
    )


def extract_profile(text: str) -> ExtractedProfile:
    llm = get_llm_provider()
    if llm.available:
        valid_roles = list(ROLE_SKILLS.keys())
        system = (
            "You extract structured learner profile data from free text for an "
            "adaptive learning platform. Respond with ONLY a JSON object, no "
            "prose, no markdown fences. Schema: {"
            '"goal": string, "target_role": one of ' + str(valid_roles) + ", "
            '"current_skills": string[] (lowercase skill keywords), '
            '"experience_level": "beginner"|"intermediate"|"advanced", '
            '"timeline_weeks": integer, "weekly_hours": number, '
            '"interests": string[], "learning_preferences": string[], '
            '"constraints": string[] }'
        )
        result = llm.complete_json(system, text, max_tokens=500)
        if result.ok and isinstance(result.data, dict):
            try:
                data = result.data
                return ExtractedProfile(
                    goal=data.get("goal", text),
                    target_role=data.get("target_role") or _detect_role(text.lower()),
                    current_skills=data.get("current_skills", []) or [],
                    experience_level=data.get("experience_level", "beginner"),
                    timeline_weeks=int(data.get("timeline_weeks") or 24),
                    weekly_hours=float(data.get("weekly_hours") or 8.0),
                    interests=data.get("interests", []) or [],
                    learning_preferences=data.get("learning_preferences", []) or ["project-first"],
                    constraints=data.get("constraints", []) or [],
                    confidence=0.85,
                    source="llm",
                )
            except Exception:
                pass
    return _rule_based_extract(text)
