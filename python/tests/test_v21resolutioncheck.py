from __future__ import annotations

from pathlib import Path

from v21resolution_check import run_check


def test_v21resolution_check_reports_resolved_state(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["resolution_state"] == "resolu"
    assert result["resolution_confidence"] == "haute"
    assert result["map_verdict"] == "supported"
    assert result["sensitivity_verdict"] == "supported"
    assert result["robust_verdict"] == "borderline"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
