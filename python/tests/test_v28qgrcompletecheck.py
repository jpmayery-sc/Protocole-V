from __future__ import annotations

from pathlib import Path

from v28qgrcomplete_check import run_check


def test_v28_qgr_complete_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-QGR-COMPLETE"
    assert result["verdict"] == "supported"
    assert result["qgrcompleteconsistency"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
