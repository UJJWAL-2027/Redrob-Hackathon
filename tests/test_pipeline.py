from __future__ import annotations

import csv
import json

from redrob_ranker.config import RankerConfig
from redrob_ranker.pipeline import RankingPipeline
from redrob_ranker.submission import write_submission


def test_pipeline_ranks_strong_candidate_first(tmp_path, make_candidate):
    strong = make_candidate(candidate_id="CAND_0000001")
    weak = make_candidate(
        candidate_id="CAND_0000002",
        profile={"current_title": "Backend Engineer", "years_of_experience": 6.5, "location": "Toronto", "country": "Canada"},
        career_history=[
            {
                "company": "ServiceCo",
                "title": "Backend Engineer",
                "start_date": "2020-01-01",
                "end_date": None,
                "duration_months": 77,
                "is_current": True,
                "industry": "IT Services",
                "company_size": "10001+",
                "description": "Built APIs and SQL reporting dashboards. Some adjacent exposure to ML teams.",
            }
        ],
        skills=[{"name": "Python", "proficiency": "advanced", "endorsements": 12, "duration_months": 72}],
    )
    data = tmp_path / "candidates.json"
    data.write_text(json.dumps([weak, strong]), encoding="utf-8")

    ranked = RankingPipeline(RankerConfig(top_k=1, stage1_keep=10, semantic_keep=10)).rank_file(data)

    assert ranked[0].score.candidate_id == "CAND_0000001"


def test_submission_writer_outputs_required_columns(tmp_path, make_candidate):
    data = tmp_path / "candidates.json"
    data.write_text(json.dumps([make_candidate(candidate_id="CAND_0000001")]), encoding="utf-8")
    ranked = RankingPipeline(RankerConfig(top_k=1, stage1_keep=10, semantic_keep=10)).rank_file(data)
    out = tmp_path / "submission.csv"

    write_submission(ranked, out, RankerConfig(top_k=1))

    with open(out, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == ["candidate_id", "rank", "score", "reasoning"]
    assert rows[1][0] == "CAND_0000001"
    assert rows[1][1] == "1"
    assert rows[1][3]
