"""Final comparison logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .behavior import BehaviorAssessment
from .capability_graph import CapabilityGraph
from .evidence import CandidateEvidence
from .fraud import FraudAssessment
from .scoring import CandidateScore


@dataclass
class CandidateEvaluation:
    candidate: dict[str, Any]
    evidence: CandidateEvidence
    graph: CapabilityGraph
    behavior: BehaviorAssessment
    fraud: FraudAssessment
    score: CandidateScore


def ranking_key(evaluation: CandidateEvaluation) -> tuple:
    score = evaluation.score
    return (
        score.final_score,
        score.integrity,
        score.capability_match,
        score.production_experience,
        score.retrieval_strength,
        score.evaluation_strength,
        score.behavior_score,
        -_candidate_number(score.candidate_id),
    )


def sort_evaluations(evaluations: list[CandidateEvaluation]) -> list[CandidateEvaluation]:
    return sorted(evaluations, key=ranking_key, reverse=True)


def _candidate_number(candidate_id: str) -> int:
    try:
        return int(candidate_id.split("_", 1)[1])
    except (IndexError, ValueError):
        return 10**9
