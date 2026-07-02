"""Small text utilities used by the offline ranker."""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.\-]*")


def normalize(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


@lru_cache(maxsize=4096)
def normalize_phrase(text: str) -> str:
    return normalize(text)


def tokens(text: object) -> list[str]:
    return TOKEN_RE.findall(normalize(text))


def token_set(text: object) -> set[str]:
    return set(tokens(text))


def phrase_hits(text: object, phrases: Iterable[str]) -> list[str]:
    normalized_text = normalize(text)
    return phrase_hits_prepared(normalized_text, set(TOKEN_RE.findall(normalized_text)), phrases)


def phrase_hits_prepared(normalized_text: str, words: set[str], phrases: Iterable[str]) -> list[str]:
    normalized = f" {normalized_text} "
    hits: list[str] = []
    for phrase in phrases:
        candidate = normalize_phrase(str(phrase))
        if not candidate:
            continue
        if " " in candidate:
            if f" {candidate} " in normalized:
                hits.append(phrase)
        elif candidate in words:
            hits.append(phrase)
    return hits


def bounded(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def saturating_log(value: float, scale: float) -> float:
    if value <= 0:
        return 0.0
    return bounded(math.log1p(value) / math.log1p(scale))


def sentence_with_hit(text: str, phrases: Iterable[str], max_chars: int = 170) -> str:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    phrase_list = list(phrases)
    for chunk in chunks:
        if phrase_hits(chunk, phrase_list):
            return trim(chunk, max_chars)
    return trim(text, max_chars)


def trim(text: str, max_chars: int = 170) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) <= max_chars:
        return cleaned
    shortened = cleaned[: max_chars - 1].rsplit(" ", 1)[0]
    return f"{shortened}..."


def cosine_from_counters(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(value * right.get(term, 0.0) for term, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
