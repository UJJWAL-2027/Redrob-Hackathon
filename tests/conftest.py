from __future__ import annotations

from copy import deepcopy

import pytest


@pytest.fixture
def make_candidate():
    def _make_candidate(**overrides):
        return _candidate(**overrides)

    return _make_candidate


def _candidate(**overrides):
    candidate = {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Test Candidate",
            "headline": "Senior AI Engineer building retrieval systems",
            "summary": "Hands-on ML engineer who has shipped production retrieval and ranking systems.",
            "location": "Pune",
            "country": "India",
            "years_of_experience": 7.0,
            "current_title": "Senior AI Engineer",
            "current_company": "ProductCo",
            "current_company_size": "201-500",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "ProductCo",
                "title": "Senior AI Engineer",
                "start_date": "2021-01-01",
                "end_date": None,
                "duration_months": 65,
                "is_current": True,
                "industry": "Software",
                "company_size": "201-500",
                "description": "Shipped a production hybrid retrieval and ranking system using embeddings, FAISS, BM25, NDCG evaluation, A/B testing, monitoring, and recruiter feedback loops.",
            }
        ],
        "education": [],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 40, "duration_months": 84},
            {"name": "FAISS", "proficiency": "advanced", "endorsements": 20, "duration_months": 36},
            {"name": "NDCG", "proficiency": "advanced", "endorsements": 12, "duration_months": 30},
        ],
        "certifications": [],
        "languages": [],
        "redrob_signals": {
            "profile_completeness_score": 94,
            "signup_date": "2025-01-01",
            "last_active_date": "2026-06-10",
            "open_to_work_flag": True,
            "profile_views_received_30d": 80,
            "applications_submitted_30d": 3,
            "recruiter_response_rate": 0.82,
            "avg_response_time_hours": 12,
            "skill_assessment_scores": {"Python": 92, "NDCG": 85},
            "connection_count": 200,
            "endorsements_received": 90,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 45, "max": 70},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "github_activity_score": 75,
            "search_appearance_30d": 160,
            "saved_by_recruiters_30d": 12,
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.7,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
        },
    }
    merged = deepcopy(candidate)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged
