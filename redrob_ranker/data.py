"""Candidate input loading and lightweight schema validation."""

from __future__ import annotations

import gzip
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class CandidateDataError(ValueError):
    pass


def iter_candidates(path: str | Path) -> Iterator[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        raise CandidateDataError(f"Candidate file not found: {source}")

    if source.suffix == ".gz":
        with gzip.open(source, "rt", encoding="utf-8") as handle:
            yield from _iter_jsonl(handle)
        return

    if source.suffix == ".jsonl":
        with open(source, "r", encoding="utf-8") as handle:
            yield from _iter_jsonl(handle)
        return

    if source.suffix == ".json":
        with open(source, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    yield item
            return
        raise CandidateDataError("JSON candidate file must contain a list of records.")

    raise CandidateDataError("Candidate file must be .json, .jsonl, or .jsonl.gz")


def _iter_jsonl(handle) -> Iterator[dict[str, Any]]:
    for line_no, line in enumerate(handle, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CandidateDataError(f"Invalid JSON on line {line_no}: {exc}") from exc
        if isinstance(item, dict):
            yield item


def validate_minimal(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("candidate_id", "profile", "career_history", "education", "skills", "redrob_signals"):
        if key not in candidate:
            errors.append(f"missing {key}")
    profile = candidate.get("profile") or {}
    if not isinstance(profile, dict):
        errors.append("profile is not an object")
    elif not profile.get("current_title"):
        errors.append("missing profile.current_title")
    career = candidate.get("career_history")
    if not isinstance(career, list) or not career:
        errors.append("career_history must be a non-empty list")
    return errors


def candidate_text(candidate: dict[str, Any], include_skills: bool = True) -> str:
    profile = candidate.get("profile") or {}
    chunks: list[str] = [
        str(profile.get("headline", "")),
        str(profile.get("summary", "")),
        str(profile.get("current_title", "")),
        str(profile.get("current_industry", "")),
    ]
    for job in candidate.get("career_history") or []:
        chunks.extend(
            [
                str(job.get("title", "")),
                str(job.get("industry", "")),
                str(job.get("description", "")),
            ]
        )
    if include_skills:
        chunks.extend(str(skill.get("name", "")) for skill in candidate.get("skills") or [])
    return " ".join(chunks)
