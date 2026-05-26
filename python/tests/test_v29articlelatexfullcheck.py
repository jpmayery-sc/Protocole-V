from __future__ import annotations

from pathlib import Path

from v29articlelatexfull_check import run_check


def test_v29_article_latex_full_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-ARTICLE-LATEX-FULL"
    assert result["verdict"] == "supported"
    assert result["readyforsubmission_final"] is True
    assert result["latexfullstructure"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
