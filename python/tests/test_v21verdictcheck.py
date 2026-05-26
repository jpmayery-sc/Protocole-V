from __future__ import annotations

from pathlib import Path

from v21verdict_check import run_check


def test_v21verdict_check_reports_global_resolution(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict_global"] == "supported"
    assert result["classification"] == "resolu"
    assert result["niveau_de_confiance"] == "haute"
    assert result["zone_critique_principale"] == "none"
    assert result["borderline"]["verdict"] == "supported"
    assert result["resolution"]["verdict"] == "supported"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()