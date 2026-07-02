"""Behavioral signal scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .config import RankerConfig
from .taxonomy import LOCATION_PREFERRED
from .text import bounded, normalize, saturating_log


@dataclass
class BehaviorAssessment:
    availability: float
    engagement: float
    trust: float
    location_fit: float
    score: float
    notes: list[str] = field(default_factory=list)


def assess_behavior(candidate: dict[str, Any], config: RankerConfig) -> BehaviorAssessment:
    profile = candidate.get("profile") or {}
    signals = candidate.get("redrob_signals") or {}
    notes: list[str] = []

    response = float(signals.get("recruiter_response_rate") or 0)
    interview = float(signals.get("interview_completion_rate") or 0)
    open_to_work = 1.0 if signals.get("open_to_work_flag") else 0.0
    notice_days = int(signals.get("notice_period_days") or 180)
    response_time = float(signals.get("avg_response_time_hours") or 999)
    active_days = _days_since(str(signals.get("last_active_date", "")), config)

    availability = (
        0.32 * open_to_work
        + 0.22 * bounded(1.0 - notice_days / 120.0)
        + 0.24 * bounded(1.0 - active_days / 180.0)
        + 0.22 * response
    )
    if notice_days <= 30:
        notes.append(f"{notice_days}-day notice")
    elif notice_days >= 90:
        notes.append(f"{notice_days}-day notice concern")
    if active_days <= 30:
        notes.append("recently active")
    elif active_days > 120:
        notes.append("stale activity")

    engagement = (
        0.26 * response
        + 0.2 * bounded(1.0 - response_time / 168.0)
        + 0.18 * interview
        + 0.12 * saturating_log(float(signals.get("profile_views_received_30d") or 0), 100)
        + 0.12 * saturating_log(float(signals.get("saved_by_recruiters_30d") or 0), 20)
        + 0.12 * saturating_log(float(signals.get("github_activity_score") or 0), 100)
    )

    completeness = float(signals.get("profile_completeness_score") or 0) / 100.0
    verified = sum(
        1.0
        for key in ("verified_email", "verified_phone", "linkedin_connected")
        if signals.get(key)
    ) / 3.0
    endorsements = saturating_log(float(signals.get("endorsements_received") or 0), 150)
    trust = 0.46 * completeness + 0.3 * verified + 0.24 * endorsements

    location = normalize(profile.get("location", ""))
    country = normalize(profile.get("country", ""))
    willing = bool(signals.get("willing_to_relocate"))
    preferred_mode = normalize(signals.get("preferred_work_mode", ""))
    if any(city in location for city in LOCATION_PREFERRED):
        location_fit = 1.0
        notes.append(f"{profile.get('location')} location fit")
    elif country == "india" and (willing or preferred_mode in {"hybrid", "flexible"}):
        location_fit = 0.82
    elif country == "india":
        location_fit = 0.68
    elif willing:
        location_fit = 0.48
    else:
        location_fit = 0.24

    score = 0.38 * availability + 0.28 * engagement + 0.2 * trust + 0.14 * location_fit
    return BehaviorAssessment(
        availability=bounded(availability),
        engagement=bounded(engagement),
        trust=bounded(trust),
        location_fit=bounded(location_fit),
        score=bounded(score),
        notes=notes[:4],
    )


def _days_since(raw: str, config: RankerConfig) -> int:
    try:
        last = date.fromisoformat(raw[:10])
        current = date(config.current_year, config.current_month, 23)
        return max(0, (current - last).days)
    except ValueError:
        return 365
