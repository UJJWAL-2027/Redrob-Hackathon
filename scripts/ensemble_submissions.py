#!/usr/bin/env python3
"""Create a weighted-rank-fusion Redrob submission and analysis report."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


FIELDNAMES = ["candidate_id", "rank", "score", "reasoning"]
SOURCE_ORDER = ("ravi", "ujjwal", "ritu")
SOURCE_WEIGHTS = {"ravi": 0.50, "ujjwal": 0.30, "ritu": 0.20}
MISSING_RANK = 150
CONCERN_PATTERN = re.compile(
    r"\b(concern|low response|response rate|notice|low experience|"
    r"limited experience|availability|inactive|not open to work)\b",
    re.IGNORECASE,
)
EVIDENCE_TERMS = (
    "retrieval",
    "ranking",
    "evaluation",
    "production",
    "vector",
    "semantic search",
    "hybrid",
    "deployed",
    "built",
    "served",
    "pipeline",
)


@dataclass(frozen=True)
class SubmissionRow:
    candidate_id: str
    rank: int
    score: float
    reasoning: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ujjwal", type=Path, required=True)
    parser.add_argument("--ravi", type=Path, required=True)
    parser.add_argument("--ritu", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--analysis-json", type=Path)
    return parser.parse_args()


def load_submission(path: Path) -> dict[str, SubmissionRow]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise ValueError(f"{path}: expected header {FIELDNAMES}, found {reader.fieldnames}")
        rows: dict[str, SubmissionRow] = {}
        ranks: set[int] = set()
        for raw in reader:
            candidate_id = raw["candidate_id"].strip()
            rank = int(raw["rank"])
            if candidate_id in rows:
                raise ValueError(f"{path}: duplicate candidate {candidate_id}")
            if rank in ranks:
                raise ValueError(f"{path}: duplicate rank {rank}")
            rows[candidate_id] = SubmissionRow(
                candidate_id=candidate_id,
                rank=rank,
                score=float(raw["score"]),
                reasoning=raw["reasoning"].strip(),
            )
            ranks.add(rank)
    if len(rows) != 100 or ranks != set(range(1, 101)):
        raise ValueError(f"{path}: expected exactly 100 candidates ranked 1 through 100")
    return rows


def normalized_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def reasoning_quality(source: str, row: SubmissionRow) -> float:
    text = row.reasoning.lower()
    evidence_density = sum(term in text for term in EVIDENCE_TERMS)
    specificity = min(len(row.reasoning), 700) / 700
    quoted_evidence = min(row.reasoning.count('"'), 4) / 4
    rank_confidence = (101 - row.rank) / 100
    return (
        2.2 * evidence_density
        + 1.4 * specificity
        + 1.2 * quoted_evidence
        + 1.0 * rank_confidence
        + SOURCE_WEIGHTS[source]
    )


def split_clauses(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|;\s+", text)
    return [part.strip(" ,;") for part in parts if part.strip(" ,;")]


def concern_category(text: str) -> str:
    lowered = text.lower()
    if "notice" in lowered:
        return "notice"
    if "response" in lowered:
        return "response"
    if "experience" in lowered:
        return "experience"
    if "availability" in lowered or "open to work" in lowered:
        return "availability"
    return "other"


def extract_concerns(rows: list[SubmissionRow]) -> list[tuple[str, str]]:
    concerns: list[tuple[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        for clause in split_clauses(row.reasoning):
            if not CONCERN_PATTERN.search(clause):
                continue
            key = concern_category(clause)
            if key not in seen:
                concerns.append((key, clause.rstrip(".") + "."))
                seen.add(key)
    return concerns


def best_supplement(base: str, rows: list[SubmissionRow]) -> str | None:
    base_tokens = normalized_tokens(base)
    candidates: list[tuple[float, str]] = []
    for row in rows:
        for clause in split_clauses(row.reasoning):
            clause_tokens = normalized_tokens(clause)
            if len(clause_tokens) < 5 or CONCERN_PATTERN.search(clause):
                continue
            overlap = len(base_tokens & clause_tokens) / max(1, len(clause_tokens))
            evidence_count = sum(term in clause.lower() for term in EVIDENCE_TERMS)
            if overlap < 0.45 and evidence_count:
                candidates.append((evidence_count - overlap, clause.rstrip(".") + "."))
    return max(candidates, default=(0.0, ""))[1] or None


def merge_reasoning(
    candidate_id: str,
    submissions: dict[str, dict[str, SubmissionRow]],
) -> tuple[str, str]:
    available = [
        (source, submissions[source][candidate_id])
        for source in SOURCE_ORDER
        if candidate_id in submissions[source]
    ]
    base_source, base_row = max(
        available,
        key=lambda item: reasoning_quality(item[0], item[1]),
    )
    reasoning = base_row.reasoning.strip()
    if reasoning and reasoning[-1] not in ".!?":
        reasoning += "."

    other_rows = [row for source, row in available if source != base_source]
    concerns = extract_concerns(other_rows)
    base_concern_categories = {
        concern_category(clause)
        for clause in split_clauses(reasoning)
        if CONCERN_PATTERN.search(clause)
    }
    for category, concern in concerns:
        if category not in base_concern_categories:
            reasoning += f" {concern}"
            break

    base_evidence_count = sum(term in reasoning.lower() for term in EVIDENCE_TERMS)
    if not concerns and (len(reasoning) < 220 or base_evidence_count <= 1):
        supplement = best_supplement(reasoning, other_rows)
        if supplement:
            reasoning += f" Additional corroboration: {supplement}"

    return reasoning[:1400].strip(), base_source


def rank_fusion(
    submissions: dict[str, dict[str, SubmissionRow]],
) -> list[dict[str, object]]:
    candidate_ids = set().union(*(set(rows) for rows in submissions.values()))
    fused: list[dict[str, object]] = []
    for candidate_id in candidate_ids:
        source_ranks = {
            source: submissions[source].get(
                candidate_id,
                SubmissionRow(candidate_id, MISSING_RANK, 0.0, ""),
            ).rank
            for source in SOURCE_ORDER
        }
        fused_rank = sum(
            SOURCE_WEIGHTS[source] * source_ranks[source] for source in SOURCE_ORDER
        )
        reasoning, reasoning_source = merge_reasoning(candidate_id, submissions)
        fused.append(
            {
                "candidate_id": candidate_id,
                "fused_rank": fused_rank,
                "source_ranks": source_ranks,
                "source_count": sum(rank != MISSING_RANK for rank in source_ranks.values()),
                "reasoning": reasoning,
                "reasoning_source": reasoning_source,
            }
        )
    fused.sort(
        key=lambda item: (
            item["fused_rank"],
            min(item["source_ranks"].values()),
            item["candidate_id"],
        )
    )
    return fused


def write_submission(path: Path, top_candidates: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for rank, candidate in enumerate(top_candidates, start=1):
            score = 1 - ((rank - 1) / 100)
            writer.writerow(
                {
                    "candidate_id": candidate["candidate_id"],
                    "rank": rank,
                    "score": f"{score:.2f}",
                    "reasoning": candidate["reasoning"],
                }
            )


def candidate_summary(candidate: dict[str, object], rank: int | None = None) -> dict[str, object]:
    result = {
        "candidate_id": candidate["candidate_id"],
        "fused_rank": round(float(candidate["fused_rank"]), 2),
        "rank_ujjwal": candidate["source_ranks"]["ujjwal"],
        "rank_ravi": candidate["source_ranks"]["ravi"],
        "rank_ritu": candidate["source_ranks"]["ritu"],
        "source_count": candidate["source_count"],
        "reasoning_source": candidate["reasoning_source"],
    }
    if rank is not None:
        result["final_rank"] = rank
        result["score"] = round(1 - ((rank - 1) / 100), 2)
    return result


def build_analysis(
    submissions: dict[str, dict[str, SubmissionRow]],
    fused: list[dict[str, object]],
) -> dict[str, object]:
    top = fused[:100]
    final_ids = {candidate["candidate_id"] for candidate in top}
    original_ids = set(submissions["ravi"])
    newly_introduced = [
        candidate_summary(candidate, rank)
        for rank, candidate in enumerate(top, start=1)
        if candidate["candidate_id"] not in original_ids
    ]
    dropped_lookup = {candidate["candidate_id"]: candidate for candidate in fused}
    dropped = [
        {
            "candidate_id": candidate_id,
            "original_rank": submissions["ravi"][candidate_id].rank,
            "fused_rank": round(float(dropped_lookup[candidate_id]["fused_rank"]), 2),
            "rank_ujjwal": dropped_lookup[candidate_id]["source_ranks"]["ujjwal"],
            "rank_ravi": dropped_lookup[candidate_id]["source_ranks"]["ravi"],
            "rank_ritu": dropped_lookup[candidate_id]["source_ranks"]["ritu"],
        }
        for candidate_id in original_ids - final_ids
    ]
    dropped.sort(key=lambda item: item["original_rank"])

    risky = []
    for rank, candidate in enumerate(top, start=1):
        if candidate["candidate_id"] in original_ids:
            continue
        reasoning = str(candidate["reasoning"]).lower()
        risk_labels = []
        if candidate["source_count"] == 1:
            risk_labels.append("single-source selection")
        if re.search(r"\b(?:60|90|120|180)[-\s]?day notice\b|notice concern", reasoning):
            risk_labels.append("high notice period")
        if "low response" in reasoning:
            risk_labels.append("low response rate")
        if "low experience" in reasoning or "limited experience" in reasoning:
            risk_labels.append("low experience")
        if "stale activity" in reasoning or "inactive" in reasoning:
            risk_labels.append("stale activity")
        if "predates public" in reasoning or "unsupported" in reasoning:
            risk_labels.append("plausibility concern")
        if risk_labels:
            item = candidate_summary(candidate, rank)
            item["risk"] = ", ".join(risk_labels)
            risky.append(item)

    sets = {source: set(rows) for source, rows in submissions.items()}
    overlap = {
        "unique_candidates": len(set().union(*sets.values())),
        "all_three": len(set.intersection(*sets.values())),
        "ujjwal_ravi": len(sets["ujjwal"] & sets["ravi"]),
        "ujjwal_ritu": len(sets["ujjwal"] & sets["ritu"]),
        "ravi_ritu": len(sets["ravi"] & sets["ritu"]),
        "only_ujjwal": len(sets["ujjwal"] - sets["ravi"] - sets["ritu"]),
        "only_ravi": len(sets["ravi"] - sets["ujjwal"] - sets["ritu"]),
        "only_ritu": len(sets["ritu"] - sets["ujjwal"] - sets["ravi"]),
        "final_from_all_three": sum(candidate["source_count"] == 3 for candidate in top),
        "final_from_two": sum(candidate["source_count"] == 2 for candidate in top),
        "final_from_one": sum(candidate["source_count"] == 1 for candidate in top),
    }
    return {
        "overlap": overlap,
        "top_20": [
            candidate_summary(candidate, rank)
            for rank, candidate in enumerate(top[:20], start=1)
        ],
        "newly_introduced": newly_introduced,
        "dropped_from_ravi": dropped,
        "possible_risky_additions": risky,
    }


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_None._"
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def write_report(path: Path, analysis: dict[str, object], output_path: Path) -> None:
    overlap = analysis["overlap"]
    lines = [
        "# Redrob Weighted Rank Fusion Analysis",
        "",
        "Weights: Ravi 0.50, Ujjwal 0.30, Ritu 0.20. Missing candidates receive rank 150.",
        "",
        "## Overlap",
        "",
        f"- Unique candidates across inputs: {overlap['unique_candidates']}",
        f"- Present in all three: {overlap['all_three']}",
        f"- Pairwise overlap: Ujjwal/Ravi {overlap['ujjwal_ravi']}, "
        f"Ujjwal/Ritu {overlap['ujjwal_ritu']}, Ravi/Ritu {overlap['ravi_ritu']}",
        f"- Final 100 consensus: all three {overlap['final_from_all_three']}, "
        f"two sources {overlap['final_from_two']}, one source {overlap['final_from_one']}",
        "",
        "## Top 20",
        "",
        markdown_table(
            analysis["top_20"],
            [
                "final_rank",
                "candidate_id",
                "fused_rank",
                "rank_ujjwal",
                "rank_ravi",
                "rank_ritu",
                "source_count",
            ],
        ),
        "",
        "## Newly Introduced vs Ravi",
        "",
        markdown_table(
            analysis["newly_introduced"],
            [
                "final_rank",
                "candidate_id",
                "fused_rank",
                "rank_ravi",
                "rank_ritu",
                "source_count",
            ],
        ),
        "",
        "## Dropped from Ravi",
        "",
        markdown_table(
            analysis["dropped_from_ravi"],
            ["candidate_id", "original_rank", "fused_rank", "rank_ujjwal", "rank_ritu"],
        ),
        "",
        "## Possible Risky Additions",
        "",
        markdown_table(
            analysis["possible_risky_additions"],
            [
                "final_rank",
                "candidate_id",
                "fused_rank",
                "source_count",
                "risk",
            ],
        ),
        "",
        f"Final CSV: `{output_path}`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    submissions = {
        "ujjwal": load_submission(args.ujjwal),
        "ravi": load_submission(args.ravi),
        "ritu": load_submission(args.ritu),
    }
    fused = rank_fusion(submissions)
    top_candidates = fused[:100]
    write_submission(args.output, top_candidates)
    analysis = build_analysis(submissions, fused)
    write_report(args.report, analysis, args.output)
    if args.analysis_json:
        args.analysis_json.parent.mkdir(parents=True, exist_ok=True)
        args.analysis_json.write_text(
            json.dumps(analysis, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
