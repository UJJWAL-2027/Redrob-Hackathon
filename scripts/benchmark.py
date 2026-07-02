#!/usr/bin/env python3
"""Quick runtime benchmark for the ranker."""

from __future__ import annotations

import argparse
import time

from redrob_ranker.config import RankerConfig
from redrob_ranker.pipeline import RankingPipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark ranking throughput.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--top-k", type=int, default=100)
    args = parser.parse_args()

    start = time.perf_counter()
    evaluations = RankingPipeline(RankerConfig(top_k=args.top_k)).rank_file(args.candidates)
    elapsed = time.perf_counter() - start
    print(f"ranked_candidates={len(evaluations)} elapsed_seconds={elapsed:.3f}")
    if evaluations:
        print(f"top_candidate={evaluations[0].score.candidate_id} score={evaluations[0].score.final_score:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
