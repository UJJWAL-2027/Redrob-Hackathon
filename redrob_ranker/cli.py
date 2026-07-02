"""Command line interface."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from .config import RankerConfig
from .pipeline import RankingPipeline
from .submission import write_submission


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank Redrob candidates offline and write a submission CSV.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl, candidates.jsonl.gz, or sample JSON.")
    parser.add_argument("--out", required=True, help="Output CSV path.")
    parser.add_argument("--top-k", type=int, default=100, help="Number of ranked rows to write. Official submissions require 100.")
    parser.add_argument("--stage1-keep", type=int, default=20000, help="Cheap-stage candidates retained before semantic reranking.")
    parser.add_argument("--semantic-keep", type=int, default=4000, help="Candidates considered by local semantic reranker.")
    parser.add_argument("--validate-with", help="Optional path to official validate_submission.py.")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(name)s: %(message)s")
    config = RankerConfig(
        top_k=args.top_k,
        stage1_keep=args.stage1_keep,
        semantic_keep=args.semantic_keep,
    )
    pipeline = RankingPipeline(config=config)
    evaluations = pipeline.rank_file(args.candidates)
    write_submission(evaluations, args.out, config)
    logging.info("wrote %s ranked candidates to %s", args.top_k, args.out)

    if args.validate_with:
        validator = Path(args.validate_with)
        if not validator.exists():
            raise FileNotFoundError(f"validator not found: {validator}")
        result = subprocess.run([sys.executable, str(validator), args.out], check=False, text=True)
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
