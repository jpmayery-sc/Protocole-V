from __future__ import annotations

from pathlib import Path

from v26publication_check import run_check


def test_v26_publication_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-PUBLICATION"
    assert result["verdict"] == "supported"
    assert result["readyforsubmission"] is True
    assert result["publication_structure"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
