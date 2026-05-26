from __future__ import annotations

from pathlib import Path

from alphaenergyrunning_check import run_check


def test_alphaenergyrunning_check_supports_running_coupling(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["running_coupling_ok"] is True
    assert result["small_slope_ok"] is True
    assert result["measured"]["sign"] == "positive"
    assert result["measured"]["dalphadE"] > 0
    assert result["measured"]["alpha_E2"] > result["measured"]["alpha_E1"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_alphaenergyrunning_check_reports_small_positive_slope(tmp_path):
    result = run_check(tmp_path)

    assert 0 < result["measured"]["dalphadE"] < 1.0e-4
    assert result["case_control"] == "valeurs tabulees de alpha(E)"