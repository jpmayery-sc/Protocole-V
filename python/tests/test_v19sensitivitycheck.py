from __future__ import annotations

from pathlib import Path

from v19sensitivity_check import run_check


def test_v19sensitivity_check_reports_supported_ranking(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["top2_stable"] is True
    assert result["ranking"][0]["parameter"] == "alpha0"
    assert result["ranking"][0]["abs_derivative"] > result["median_abs_derivative"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v19sensitivity_check_tracks_all_parameters(tmp_path):
    result = run_check(tmp_path)

    parameters = [row["parameter"] for row in result["rows"]]
    assert parameters == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]