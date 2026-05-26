from __future__ import annotations

from pathlib import Path

from v12alpha_check import run_check


def test_v12alpha_check_falsifies_strict_band(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "falsifie"
    assert result["measured"]["strict_band_ok"] is False
    assert result["measured"]["derivative_r_ok"] is True
    assert result["measured"]["surface_present_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v12alpha_check_max_deviation_is_large():
    from v12alpha_check import evaluate_alpha_bounds

    result = evaluate_alpha_bounds()
    assert result["max_deviation"] > 1.0e-8