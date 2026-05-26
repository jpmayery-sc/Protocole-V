from __future__ import annotations

from pathlib import Path

from v7electronic_check import run_check


def test_v7electronic_check_supports_extrapolated_response(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["monotone_ok"] is True
    assert result["positive_ok"] is True
    assert result["saturation_absent_ok"] is True
    assert result["critical_floor_ok"] is True
    assert result["fit_quality_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v7electronic_check_reports_strong_decay(tmp_path):
    result = run_check(tmp_path)

    extrapolated = result["extrapolated"]
    kappas = [item["kappa"] for item in extrapolated]
    assert kappas[0] > kappas[1] > kappas[2]
    assert kappas[2] > 1.0e-06