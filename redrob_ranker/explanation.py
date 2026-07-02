"""Reasoning generation grounded only in extracted candidate evidence."""

from __future__ import annotations

from .comparator import CandidateEvaluation
from .text import trim


def generate_reasoning(evaluation: CandidateEvaluation, rank: int) -> str:
    profile = evaluation.candidate.get("profile") or {}
    score = evaluation.score
    evidence = evaluation.evidence
    parts: list[str] = []

    title = profile.get("current_title") or evidence.title or "candidate"
    company = profile.get("current_company") or evidence.company
    years = profile.get("years_of_experience")
    intro = f"{title} with {years:.1f} years" if isinstance(years, (int, float)) else f"{title}"
    if company:
        intro += f" at {company}"

    strengths = []
    for capability in ("retrieval_systems", "vector_infrastructure", "ranking_evaluation", "production_ml", "python_backend"):
        items = sorted(evidence.capability_evidence.get(capability) or [], key=lambda found: found.strength, reverse=True)
        career_items = [item for item in items if item.source == "career"]
        item = career_items[0] if career_items else (items[0] if items else None)
        if item and len(strengths) < 2:
            label = capability.replace("_", " ")
            if item.source == "career" and item.company:
                strengths.append(f"{label} evidence from {item.company}: \"{trim(item.text, 110)}\"")
            elif item.source == "skills":
                strengths.append(f"{label} skills claim: \"{trim(item.text, 80)}\"")
            else:
                strengths.append(f"{label} supporting claim: \"{trim(item.text, 100)}\"")

    if strengths:
        parts.append(f"{intro}; " + "; ".join(strengths) + ".")
    else:
        parts.append(f"{intro}; limited direct retrieval/ranking evidence, so the rank is driven by adjacent engineering signals.")

    modifiers = []
    if score.production_experience >= 0.6:
        modifiers.append("production ownership is a strong positive")
    elif score.production_experience < 0.35:
        modifiers.append("production deployment evidence is thin")
    if score.evaluation_strength >= 0.45:
        modifiers.append("ranking/evaluation experience matches the JD")
    elif score.evaluation_strength < 0.2:
        modifiers.append("ranking evaluation is a gap")
    if evaluation.behavior.notes:
        modifiers.append(", ".join(evaluation.behavior.notes[:2]))
    if evidence.aspirational_ai_score > 0.35:
        modifiers.append("AI experience appears aspirational rather than professional")
    if evaluation.fraud.flags and rank <= 100:
        modifiers.append(f"concern: {evaluation.fraud.flags[0]}")

    if modifiers:
        parts.append("; ".join(modifiers) + ".")

    reasoning = " ".join(parts)
    return trim(reasoning, 500)
