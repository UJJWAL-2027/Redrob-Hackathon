"""Capability graph construction and coverage scoring."""

from __future__ import annotations

from dataclasses import dataclass

from .evidence import CandidateEvidence
from .jd import JobProfile
from .taxonomy import CAPABILITIES
from .text import bounded


@dataclass
class CapabilityGraph:
    scores: dict[str, float]
    coverage: float
    critical_coverage: float
    depth: float


CRITICAL = ("retrieval_systems", "vector_infrastructure", "ranking_evaluation", "production_ml")


def build_capability_graph(evidence: CandidateEvidence, job: JobProfile) -> CapabilityGraph:
    weighted_total = 0.0
    possible_total = 0.0
    scores: dict[str, float] = {}
    for capability in CAPABILITIES:
        score = bounded(evidence.capability_scores.get(capability.name, 0.0))
        scores[capability.name] = score
        weighted_total += score * capability.weight
        possible_total += capability.weight
    coverage = weighted_total / possible_total if possible_total else 0.0
    critical_coverage = sum(scores.get(name, 0.0) for name in CRITICAL) / len(CRITICAL)
    strong_count = sum(1 for value in scores.values() if value >= 0.55)
    depth = bounded((strong_count / 5.0) * 0.6 + critical_coverage * 0.4)
    return CapabilityGraph(
        scores=scores,
        coverage=bounded(coverage),
        critical_coverage=bounded(critical_coverage),
        depth=depth,
    )
