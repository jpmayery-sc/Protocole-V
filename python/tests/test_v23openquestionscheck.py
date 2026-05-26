from __future__ import annotations

from pathlib import Path

from v23openquestions_check import run_check


def test_v23_open_questions_check_reports_questions(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert len(result["openquestionslist"]) >= 3
    assert result["priority_ranking"][0]["priority"] == 1
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()