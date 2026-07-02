from __future__ import annotations

from redrob_ranker.config import RankerConfig
from redrob_ranker.evidence import extract_evidence
from redrob_ranker.fraud import assess_fraud


def test_career_evidence_drives_retrieval_capabilities(make_candidate):
    candidate = make_candidate()
    evidence = extract_evidence(candidate)

    assert evidence.capability_scores["retrieval_systems"] > 0.5
    assert evidence.capability_scores["ranking_evaluation"] > 0.5
    assert evidence.production_score > 0.5


def test_unsupported_keyword_stuffer_gets_penalized(make_candidate):
    candidate = make_candidate(
        profile={
            "current_title": "Marketing Manager",
            "headline": "AI leader with every modern framework",
            "summary": "Expert in Pinecone, FAISS, RAG, LangChain, Qdrant, Milvus, LLMs, LoRA, QLoRA.",
        },
        career_history=[
            {
                "company": "BrandCo",
                "title": "Marketing Manager",
                "start_date": "2021-01-01",
                "end_date": None,
                "duration_months": 65,
                "is_current": True,
                "industry": "Marketing",
                "company_size": "201-500",
                "description": "Managed campaigns, brand positioning, and content calendars for B2B products.",
            }
        ],
        skills=[
            {"name": "Pinecone", "proficiency": "expert", "endorsements": 1, "duration_months": 0},
            {"name": "FAISS", "proficiency": "expert", "endorsements": 1, "duration_months": 0},
            {"name": "LangChain", "proficiency": "expert", "endorsements": 1, "duration_months": 2},
            {"name": "Qdrant", "proficiency": "expert", "endorsements": 1, "duration_months": 0},
            {"name": "Milvus", "proficiency": "expert", "endorsements": 1, "duration_months": 0},
        ],
    )

    evidence = extract_evidence(candidate)
    fraud = assess_fraud(candidate, evidence, RankerConfig())

    assert fraud.integrity < 0.55
    assert fraud.flags
