"""Cascading offline ranking pipeline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .behavior import assess_behavior
from .capability_graph import build_capability_graph
from .comparator import CandidateEvaluation, sort_evaluations
from .config import RankerConfig
from .data import candidate_text, iter_candidates, validate_minimal
from .evidence import extract_evidence
from .fraud import assess_fraud
from .jd import JobProfile, default_job_profile
from .scoring import apply_semantic, compute_base_score
from .semantic import SemanticMatcher
from .taxonomy import NON_ENGINEERING_TITLES
from .text import normalize, phrase_hits

LOGGER = logging.getLogger(__name__)


class RankingPipeline:
    def __init__(self, config: RankerConfig | None = None, job: JobProfile | None = None) -> None:
        self.config = config or RankerConfig()
        self.job = job or default_job_profile()

    def rank_file(self, candidate_path: str | Path) -> list[CandidateEvaluation]:
        cheap_stage: list[CandidateEvaluation] = []
        seen = 0
        rejected = 0
        for candidate in iter_candidates(candidate_path):
            seen += 1
            evaluation = self._evaluate_candidate(candidate)
            if evaluation is None:
                rejected += 1
                continue
            cheap_stage.append(evaluation)
            if len(cheap_stage) > self.config.stage1_keep * 2:
                cheap_stage = sort_evaluations(cheap_stage)[: self.config.stage1_keep]
            if seen % 10000 == 0:
                LOGGER.info("parsed=%s retained=%s rejected=%s", seen, len(cheap_stage), rejected)

        LOGGER.info("parsed=%s retained_after_hard_filters=%s rejected=%s", seen, len(cheap_stage), rejected)
        cheap_stage = sort_evaluations(cheap_stage)[: self.config.stage1_keep]
        return self._semantic_rerank(cheap_stage)

    def _evaluate_candidate(self, candidate: dict[str, Any]) -> CandidateEvaluation | None:
        if validate_minimal(candidate):
            return None
        evidence = extract_evidence(candidate)
        if self._hard_reject(candidate, evidence):
            return None
        fraud = assess_fraud(candidate, evidence, self.config)
        if fraud.remove:
            return None
        behavior = assess_behavior(candidate, self.config)
        graph = build_capability_graph(evidence, self.job)
        score = compute_base_score(evidence, graph, behavior, fraud, self.config)
        return CandidateEvaluation(candidate, evidence, graph, behavior, fraud, score)

    def _semantic_rerank(self, evaluations: list[CandidateEvaluation]) -> list[CandidateEvaluation]:
        shortlist = sort_evaluations(evaluations)
        semantic_pool = shortlist[: self.config.semantic_keep]
        documents = [candidate_text(item.candidate, include_skills=False) for item in semantic_pool]
        matcher = SemanticMatcher.fit(self.job, documents)
        for evaluation in semantic_pool:
            semantic = matcher.score(candidate_text(evaluation.candidate, include_skills=False))
            apply_semantic(evaluation.score, semantic)
        reranked_pool = sort_evaluations(semantic_pool)
        tail = shortlist[self.config.semantic_keep :]
        return sort_evaluations(reranked_pool + tail)

    def _hard_reject(self, candidate: dict[str, Any], evidence) -> bool:
        years = evidence.years
        if years < self.config.hard_filter_min_years:
            return True
        if years > self.config.hard_filter_max_years and evidence.production_score < 0.45:
            return True
        capability_total = sum(evidence.capability_scores.values())
        title = normalize(evidence.title)
        critical_capability = max(
            evidence.capability_scores.get("retrieval_systems", 0.0),
            evidence.capability_scores.get("vector_infrastructure", 0.0),
            evidence.capability_scores.get("ranking_evaluation", 0.0),
            evidence.capability_scores.get("production_ml", 0.0),
        )
        if phrase_hits(title, NON_ENGINEERING_TITLES) and critical_capability < 0.28:
            return True
        if capability_total < 0.32 and not phrase_hits(title, ("engineer", "scientist", "developer", "architect")):
            return True
        if capability_total < 0.2 and evidence.production_score < 0.2:
            return True
        return False
