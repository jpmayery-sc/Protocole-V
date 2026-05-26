from __future__ import annotations

from pathlib import Path

from v27publicationadvanced_check import run_check


def test_v27_publication_advanced_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V27-ARTICLE-AVANCÉ"
    assert result["verdict"] == "supported"
    assert result["readyforsubmission_advanced"] is True
    assert result["publicationadvancedstructure"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
