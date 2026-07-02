"""Lightweight local semantic reranking after aggressive filtering."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .jd import JobProfile
from .text import cosine_from_counters, tokens


@dataclass
class SemanticMatcher:
    idf: dict[str, float]
    job_vector: Counter[str]

    @classmethod
    def fit(cls, job: JobProfile, documents: list[str], max_terms: int = 3500) -> "SemanticMatcher":
        all_docs = [job.raw_text, *documents]
        df: Counter[str] = Counter()
        for doc in all_docs:
            df.update(set(_semantic_terms(doc)))
        total = len(all_docs)
        idf = {term: math.log((1 + total) / (1 + freq)) + 1.0 for term, freq in df.items()}
        allowed = set(term for term, _ in Counter(df).most_common(max_terms))
        idf = {term: value for term, value in idf.items() if term in allowed}
        return cls(idf=idf, job_vector=_tfidf(job.raw_text, idf))

    def score(self, text: str) -> float:
        return cosine_from_counters(self.job_vector, _tfidf(text, self.idf))


def _semantic_terms(text: str) -> list[str]:
    raw = [term for term in tokens(text) if len(term) > 2]
    bigrams = [f"{left}_{right}" for left, right in zip(raw, raw[1:], strict=False)]
    return raw + bigrams


def _tfidf(text: str, idf: dict[str, float]) -> Counter[str]:
    counts = Counter(term for term in _semantic_terms(text) if term in idf)
    for term in list(counts):
        counts[term] *= idf[term]
    return counts
