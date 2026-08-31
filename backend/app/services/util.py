from __future__ import annotations


def status_for_confidence(conf: float) -> str:
    """AI-estimated proficiency band. See spec section 2 — explicitly NOT a
    scientifically validated psychometric scale, just a labeled heuristic."""
    if conf < 20:
        return "unknown"
    if conf < 40:
        return "beginner"
    if conf < 60:
        return "developing"
    if conf < 80:
        return "proficient"
    return "strong"


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))
