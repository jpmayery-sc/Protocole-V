from __future__ import annotations

from pathlib import Path

from alphageometricport_check import run_check


def test_alphageometricport_check_supports_geometric_port(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["exact_claim_ok"] is False
    assert result["geometric_port_ok"] is True
    assert result["measured"]["delta_Dtheta_rad"] != 0
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_alphageometricport_check_reports_small_delta_theta_gap(tmp_path):
    result = run_check(tmp_path)

    assert abs(result["measured"]["delta_Dtheta_rad"]) < 2.0e-5
    assert result["case_control"] == "alpha_ref vs 1/137"