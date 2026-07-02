"""Configuration for the cascading ranking pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RankerConfig:
    top_k: int = 100
    stage1_keep: int = 20000
    semantic_keep: int = 4000
    current_year: int = 2026
    current_month: int = 6
    minimum_reasoning_chars: int = 25
    hard_filter_min_years: float = 3.0
    hard_filter_max_years: float = 15.0
    output_score_decimals: int = 6

    @property
    def current_month_index(self) -> int:
        return self.current_year * 12 + self.current_month
