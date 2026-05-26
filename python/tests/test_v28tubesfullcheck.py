from __future__ import annotations

from pathlib import Path

from v28tubesfull_check import run_check


def test_v28_tubes_full_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-TUBES-FULL"
    assert result["verdict"] == "supported"
    assert result["tubemodemap"] is True
    assert result["fulltubeequations"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
