from __future__ import annotations

from pathlib import Path

from v28articlelatex_check import run_check


def test_v28_article_latex_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-ARTICLE-LATEX"
    assert result["verdict"] == "supported"
    assert result["readyforsubmission_full"] is True
    assert result["latexarticlestructure"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
