"""Evidence extraction from profile, skills, and career history."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import taxonomy
from .data import candidate_text
from .text import TOKEN_RE, bounded, normalize, phrase_hits, phrase_hits_prepared, sentence_with_hit


SOURCE_WEIGHT = {
    "career": 1.0,
    "summary": 0.45,
    "headline": 0.3,
    "skills": 0.25,
    "assessment": 0.35,
}


@dataclass
class EvidenceItem:
    capability: str
    source: str
    strength: float
    text: str
    phrases: tuple[str, ...]
    company: str = ""
    title: str = ""


@dataclass
class CandidateEvidence:
    candidate_id: str
    title: str
    company: str
    years: float
    location: str
    country: str
    full_text: str
    work_text: str
    capability_scores: dict[str, float] = field(default_factory=dict)
    capability_evidence: dict[str, list[EvidenceItem]] = field(default_factory=dict)
    production_score: float = 0.0
    product_score: float = 0.0
    engineering_title_score: float = 0.0
    consulting_only: bool = False
    research_only_score: float = 0.0
    aspirational_ai_score: float = 0.0
    skill_claims: set[str] = field(default_factory=set)
    ai_skill_claims: set[str] = field(default_factory=set)

    def top_evidence(self, capability: str) -> EvidenceItem | None:
        items = self.capability_evidence.get(capability) or []
        if not items:
            return None
        return sorted(items, key=lambda item: item.strength, reverse=True)[0]


def extract_evidence(candidate: dict[str, Any]) -> CandidateEvidence:
    profile = candidate.get("profile") or {}
    career = candidate.get("career_history") or []
    skills = candidate.get("skills") or []
    signals = candidate.get("redrob_signals") or {}

    title = str(profile.get("current_title", ""))
    current_company = str(profile.get("current_company", ""))
    full = candidate_text(candidate, include_skills=True)
    work = candidate_text(candidate, include_skills=False)
    evidence = CandidateEvidence(
        candidate_id=str(candidate.get("candidate_id", "")),
        title=title,
        company=current_company,
        years=float(profile.get("years_of_experience") or 0.0),
        location=str(profile.get("location", "")),
        country=str(profile.get("country", "")),
        full_text=full,
        work_text=work,
    )

    normalized_title = normalize(title)
    if phrase_hits(normalized_title, taxonomy.ENGINEERING_TITLES):
        evidence.engineering_title_score = 1.0
    elif any(term in normalized_title for term in ("engineer", "developer", "architect", "scientist")):
        evidence.engineering_title_score = 0.7
    elif phrase_hits(normalized_title, taxonomy.NON_ENGINEERING_TITLES):
        evidence.engineering_title_score = 0.0
    else:
        evidence.engineering_title_score = 0.35

    companies = [normalize(job.get("company", "")) for job in career]
    industries = [normalize(job.get("industry", "")) for job in career]
    evidence.consulting_only = bool(career) and all(
        company in taxonomy.CONSULTING_COMPANIES or "services" in industry
        for company, industry in zip(companies, industries, strict=False)
    )

    summary = str(profile.get("summary", ""))
    headline = str(profile.get("headline", ""))
    _scan_text(evidence, "summary", summary, "", "")
    _scan_text(evidence, "headline", headline, "", "")

    for job in career:
        description = str(job.get("description", ""))
        job_title = str(job.get("title", ""))
        company = str(job.get("company", ""))
        _scan_text(evidence, "career", f"{job_title}. {description}", company, job_title)

    skill_names = []
    for skill in skills:
        name = str(skill.get("name", ""))
        if not name:
            continue
        skill_names.append(name)
        evidence.skill_claims.add(normalize(name))
        if phrase_hits(name, taxonomy.AI_SKILL_PHRASES):
            evidence.ai_skill_claims.add(name)
        _scan_text(evidence, "skills", name, "", "")

    assessments = signals.get("skill_assessment_scores") or {}
    if isinstance(assessments, dict):
        for name, score in assessments.items():
            if float(score or 0) >= 70:
                _scan_text(evidence, "assessment", str(name), "", "")

    production_hits = phrase_hits(work, taxonomy.PRODUCTION_PHRASES)
    evidence.production_score = bounded(len(production_hits) / 6.0)
    product_hits = phrase_hits(work, ("product", "recruiter", "marketplace", "user", "customer", "feedback"))
    evidence.product_score = bounded(len(product_hits) / 4.0)
    research_hits = phrase_hits(work, taxonomy.RESEARCH_ONLY_PHRASES)
    evidence.research_only_score = bounded(len(research_hits) / 4.0)
    aspirational_hits = phrase_hits(full, taxonomy.ASPIRATIONAL_AI_PHRASES)
    evidence.aspirational_ai_score = bounded(len(aspirational_hits) / 3.0)
    for key in list(evidence.capability_scores):
        evidence.capability_scores[key] = bounded(evidence.capability_scores[key] / 2.2)
    return evidence


def _scan_text(evidence: CandidateEvidence, source: str, text: str, company: str, title: str) -> None:
    if not text:
        return
    normalized = normalize(text)
    words = set(TOKEN_RE.findall(normalized))
    has_production_evidence = bool(phrase_hits_prepared(normalized, words, taxonomy.PRODUCTION_PHRASES))
    has_weak_claim = bool(phrase_hits_prepared(normalized, words, taxonomy.ASPIRATIONAL_AI_PHRASES))
    for capability in taxonomy.CAPABILITIES:
        hits = phrase_hits_prepared(normalized, words, capability.phrases)
        if not hits:
            continue
        source_weight = SOURCE_WEIGHT[source]
        production_bonus = 0.25 if source == "career" and has_production_evidence else 0.0
        weak_claim_penalty = 0.3 if has_weak_claim else 1.0
        strength = min(
            capability.weight,
            weak_claim_penalty * (source_weight * capability.weight * (0.45 + min(len(hits), 4) * 0.18) + production_bonus),
        )
        item = EvidenceItem(
            capability=capability.name,
            source=source,
            strength=strength,
            text=sentence_with_hit(text, hits),
            phrases=tuple(hits[:5]),
            company=company,
            title=title,
        )
        evidence.capability_evidence.setdefault(capability.name, []).append(item)
        evidence.capability_scores[capability.name] = evidence.capability_scores.get(capability.name, 0.0) + strength
