"""Submission CSV writing."""

from __future__ import annotations

import csv
from pathlib import Path

from .comparator import CandidateEvaluation
from .config import RankerConfig
from .explanation import generate_reasoning


HEADER = ["candidate_id", "rank", "score", "reasoning"]


def write_submission(
    evaluations: list[CandidateEvaluation],
    out_path: str | Path,
    config: RankerConfig,
) -> None:
    if len(evaluations) < config.top_k:
        raise ValueError(
            f"Need at least {config.top_k} candidates to write an official submission; got {len(evaluations)}."
        )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    top = evaluations[: config.top_k]
    rows: list[list[str]] = []
    unit = 10 ** (-config.output_score_decimals)
    previous_score = 1.0 + unit
    for index, evaluation in enumerate(top, start=1):
        raw_score = round(evaluation.score.final_score, config.output_score_decimals)
        safe_score = max(0.0, min(raw_score, previous_score - unit))
        previous_score = safe_score
        rows.append(
            [
                evaluation.score.candidate_id,
                str(index),
                f"{safe_score:.{config.output_score_decimals}f}",
                generate_reasoning(evaluation, index),
            ]
        )

    with open(out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)
