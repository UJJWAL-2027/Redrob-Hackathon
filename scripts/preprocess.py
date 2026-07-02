#!/usr/bin/env python3
"""Optional offline feature extraction cache for candidate files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from redrob_ranker.behavior import assess_behavior
from redrob_ranker.capability_graph import build_capability_graph
from redrob_ranker.config import RankerConfig
from redrob_ranker.data import iter_candidates, validate_minimal
from redrob_ranker.evidence import extract_evidence
from redrob_ranker.fraud import assess_fraud
from redrob_ranker.jd import default_job_profile


def main() -> int:
    parser = argparse.ArgumentParser(description="Precompute explainable candidate features as JSONL.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = RankerConfig()
    job = default_job_profile()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        for candidate in iter_candidates(args.candidates):
            if validate_minimal(candidate):
                continue
            evidence = extract_evidence(candidate)
            behavior = assess_behavior(candidate, config)
            fraud = assess_fraud(candidate, evidence, config)
            graph = build_capability_graph(evidence, job)
            row = {
                "candidate_id": candidate.get("candidate_id"),
                "capabilities": graph.scores,
                "production_score": evidence.production_score,
                "behavior_score": behavior.score,
                "integrity": fraud.integrity,
                "fraud_flags": fraud.flags,
            }
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
