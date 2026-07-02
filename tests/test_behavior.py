from __future__ import annotations

from redrob_ranker.behavior import assess_behavior
from redrob_ranker.config import RankerConfig


def test_behavior_rewards_recent_responsive_available_profiles(make_candidate):
    strong = assess_behavior(make_candidate(), RankerConfig())
    weak_candidate = make_candidate()
    weak_candidate["redrob_signals"].update(
        {
            "last_active_date": "2025-01-01",
            "open_to_work_flag": False,
            "recruiter_response_rate": 0.05,
            "avg_response_time_hours": 300,
            "notice_period_days": 120,
            "interview_completion_rate": 0.2,
        }
    )
    weak = assess_behavior(weak_candidate, RankerConfig())

    assert strong.score > weak.score
    assert strong.availability > weak.availability
