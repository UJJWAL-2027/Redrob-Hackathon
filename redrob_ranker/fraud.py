"""Fraud, plausibility, and adversarial-profile checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .config import RankerConfig
from .evidence import CandidateEvidence
from .taxonomy import AI_SKILL_PHRASES, NON_ENGINEERING_TITLES, TECH_RELEASE_YEAR
from .text import bounded, normalize, phrase_hits


@dataclass
class FraudAssessment:
    integrity: float
    penalty: float
    flags: list[str] = field(default_factory=list)
    remove: bool = False


def assess_fraud(candidate: dict[str, Any], evidence: CandidateEvidence, config: RankerConfig) -> FraudAssessment:
    flags: list[str] = []
    penalty = 0.0

    skills = candidate.get("skills") or []
    career = candidate.get("career_history") or []

    zero_month_experts = [
        str(skill.get("name", ""))
        for skill in skills
        if skill.get("proficiency") == "expert" and int(skill.get("duration_months") or 0) <= 3
    ]
    if zero_month_experts:
        flags.append(f"expert skill claims with near-zero duration: {', '.join(zero_month_experts[:3])}")
        penalty += min(0.32, 0.08 * len(zero_month_experts))

    unsupported_ai = []
    for skill in skills:
        name = str(skill.get("name", ""))
        if phrase_hits(name, AI_SKILL_PHRASES) and not phrase_hits(evidence.work_text, (name,)):
            unsupported_ai.append(name)
    if len(unsupported_ai) >= 5 and sum(evidence.capability_scores.values()) < 1.4:
        flags.append("many AI skill claims are not supported by career evidence")
        penalty += 0.22
    elif len(unsupported_ai) >= 8:
        flags.append("large unsupported AI skill list")
        penalty += 0.14

    title_text = normalize(evidence.title)
    if phrase_hits(title_text, NON_ENGINEERING_TITLES) and sum(evidence.capability_scores.values()) < 1.0:
        flags.append("non-engineering title with AI-heavy profile claims")
        penalty += 0.28

    if evidence.research_only_score > 0.6 and evidence.production_score < 0.25:
        flags.append("research-oriented profile lacks production deployment evidence")
        penalty += 0.22

    if evidence.aspirational_ai_score > 0.35 and evidence.capability_scores.get("retrieval_systems", 0) < 0.45:
        flags.append("AI/retrieval experience is described as self-learning or side-project work")
        penalty += 0.16

    if evidence.consulting_only:
        flags.append("consulting/services-only career path")
        penalty += 0.16

    timeline_penalty, timeline_flags = _timeline_checks(candidate, config)
    penalty += timeline_penalty
    flags.extend(timeline_flags)

    release_penalty, release_flags = _release_checks(skills, config)
    penalty += release_penalty
    flags.extend(release_flags)

    if _recent_langchain_only(candidate, evidence):
        flags.append("recent framework/demo AI profile without deeper retrieval evidence")
        penalty += 0.18

    penalty = bounded(penalty, 0.0, 0.85)
    integrity = 1.0 - penalty
    remove = penalty >= 0.72
    return FraudAssessment(integrity=integrity, penalty=penalty, flags=flags, remove=remove)


def _timeline_checks(candidate: dict[str, Any], config: RankerConfig) -> tuple[float, list[str]]:
    flags: list[str] = []
    penalty = 0.0
    profile = candidate.get("profile") or {}
    years = float(profile.get("years_of_experience") or 0)
    career = candidate.get("career_history") or []
    total_months = sum(max(0, int(job.get("duration_months") or 0)) for job in career)
    if years > 0 and total_months > (years * 12 * 1.45 + 12):
        flags.append("career durations materially exceed stated experience")
        penalty += 0.12

    current_jobs = [job for job in career if job.get("is_current")]
    if len(current_jobs) > 1:
        flags.append("multiple current roles")
        penalty += 0.12

    for job in career:
        start = _parse_date(str(job.get("start_date", "")))
        end_raw = job.get("end_date")
        end = _parse_date(str(end_raw)) if end_raw else None
        if start and end and end < start:
            flags.append("career role ends before it starts")
            penalty += 0.16
        if start and start.year > config.current_year:
            flags.append("future-dated career start")
            penalty += 0.16
    return penalty, flags


def _release_checks(skills: list[dict[str, Any]], config: RankerConfig) -> tuple[float, list[str]]:
    flags: list[str] = []
    penalty = 0.0
    for skill in skills:
        name = normalize(skill.get("name", ""))
        duration_months = int(skill.get("duration_months") or 0)
        if duration_months <= 0:
            continue
        implied_start_year = (config.current_month_index - duration_months) // 12
        for tech, release_year in TECH_RELEASE_YEAR.items():
            if tech in name and implied_start_year < release_year:
                flags.append(f"{skill.get('name')} duration predates public release")
                penalty += 0.12
                break
    return bounded(penalty, 0.0, 0.36), flags[:3]


def _recent_langchain_only(candidate: dict[str, Any], evidence: CandidateEvidence) -> bool:
    skills = candidate.get("skills") or []
    langchain_months = [
        int(skill.get("duration_months") or 0)
        for skill in skills
        if "langchain" in normalize(skill.get("name", ""))
    ]
    if not langchain_months:
        return False
    has_deeper_retrieval = (
        evidence.capability_scores.get("retrieval_systems", 0) >= 0.45
        and evidence.capability_scores.get("vector_infrastructure", 0) >= 0.3
    )
    return max(langchain_months) < 12 and not has_deeper_retrieval


def _parse_date(raw: str) -> date | None:
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None
