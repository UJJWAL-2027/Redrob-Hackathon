"""Candidate scoring dimensions."""

from __future__ import annotations

from dataclasses import dataclass, field

from .behavior import BehaviorAssessment
from .capability_graph import CapabilityGraph
from .config import RankerConfig
from .evidence import CandidateEvidence
from .fraud import FraudAssessment
from .text import bounded


@dataclass
class CandidateScore:
    candidate_id: str
    base_score: float
    final_score: float
    integrity: float
    capability_match: float
    production_experience: float
    retrieval_strength: float
    evaluation_strength: float
    semantic_alignment: float
    behavior_score: float
    experience_fit: float
    details: dict[str, float] = field(default_factory=dict)


def compute_base_score(
    evidence: CandidateEvidence,
    graph: CapabilityGraph,
    behavior: BehaviorAssessment,
    fraud: FraudAssessment,
    config: RankerConfig,
) -> CandidateScore:
    years = evidence.years
    if 5 <= years <= 9:
        experience_fit = 1.0
    elif 4 <= years < 5 or 9 < years <= 11:
        experience_fit = 0.78
    elif 3 <= years < 4 or 11 < years <= 13:
        experience_fit = 0.55
    else:
        experience_fit = 0.28

    retrieval_strength = (
        0.55 * graph.scores.get("retrieval_systems", 0.0)
        + 0.3 * graph.scores.get("vector_infrastructure", 0.0)
        + 0.15 * graph.scores.get("data_infrastructure", 0.0)
    )
    evaluation_strength = graph.scores.get("ranking_evaluation", 0.0)
    production_experience = bounded(
        0.42 * evidence.production_score
        + 0.25 * graph.scores.get("production_ml", 0.0)
        + 0.18 * evidence.engineering_title_score
        + 0.15 * evidence.product_score
    )
    capability_match = bounded(
        0.34 * graph.coverage
        + 0.34 * graph.critical_coverage
        + 0.16 * graph.depth
        + 0.16 * retrieval_strength
    )

    base = (
        0.28 * capability_match
        + 0.2 * retrieval_strength
        + 0.16 * evaluation_strength
        + 0.15 * production_experience
        + 0.08 * experience_fit
        + 0.08 * behavior.score
        + 0.05 * fraud.integrity
    )

    if graph.scores.get("retrieval_systems", 0.0) < 0.25:
        base *= 0.78
    if graph.scores.get("ranking_evaluation", 0.0) < 0.18:
        base *= 0.88
    if evidence.consulting_only:
        base *= 0.9
    if evidence.aspirational_ai_score > 0.35 and graph.critical_coverage < 0.35:
        base *= 0.78

    final = bounded(base * (0.72 + 0.28 * fraud.integrity))
    return CandidateScore(
        candidate_id=evidence.candidate_id,
        base_score=bounded(base),
        final_score=final,
        integrity=fraud.integrity,
        capability_match=capability_match,
        production_experience=production_experience,
        retrieval_strength=bounded(retrieval_strength),
        evaluation_strength=bounded(evaluation_strength),
        semantic_alignment=0.0,
        behavior_score=behavior.score,
        experience_fit=experience_fit,
        details={
            "coverage": graph.coverage,
            "critical_coverage": graph.critical_coverage,
            "title": evidence.engineering_title_score,
            "location": behavior.location_fit,
        },
    )


def apply_semantic(score: CandidateScore, semantic_alignment: float) -> CandidateScore:
    blended = bounded(
        0.92 * score.final_score
        + 0.08 * semantic_alignment * max(0.55, score.capability_match)
    )
    score.semantic_alignment = bounded(semantic_alignment)
    score.final_score = blended
    return score
