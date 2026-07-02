"""Job description representation."""

from __future__ import annotations

from dataclasses import dataclass

from .taxonomy import CAPABILITIES


DEFAULT_JOB_DESCRIPTION = """
Senior AI Engineer founding team role at Redrob AI. The role owns retrieval,
ranking, candidate-job matching, embeddings, hybrid search, vector databases,
LLM reranking, production Python systems, and evaluation frameworks such as
NDCG, MRR, MAP, A/B testing, and recruiter feedback loops. Strong preference
for 5-9 years of experience, product company background, production deployment,
hands-on code in the last 18 months, Pune/Noida/major Indian city availability,
and a shipper mindset. Pure research, consulting-only career paths, title
chasing, keyword-only LLM projects, and unsupported AI claims are negative.
"""


@dataclass(frozen=True)
class JobProfile:
    raw_text: str
    required_capabilities: tuple[str, ...]
    ideal_years_min: float = 5.0
    ideal_years_max: float = 9.0


def default_job_profile() -> JobProfile:
    return JobProfile(
        raw_text=DEFAULT_JOB_DESCRIPTION,
        required_capabilities=tuple(cap.name for cap in CAPABILITIES[:6]),
    )
