from __future__ import annotations

from pathlib import Path

from v21recovery_check import run_check


def test_v21recovery_check_reports_supported_recovery(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["supported_chain_length"] == 4
    assert result["bottleneck_flag"] is True
    assert result["recovery_margin"] == 1.0e-06
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v21recovery_check_has_positive_resolution_score(tmp_path):
    result = run_check(tmp_path)

    assert result["resolution_score"] > 0.0
    assert result["recovery_depth"] > 0.0