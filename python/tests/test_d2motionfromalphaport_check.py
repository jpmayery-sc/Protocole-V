from __future__ import annotations

from pathlib import Path

from d2motionfromalphaport_check import run_check


def test_d2motionfromalphaport_check_supports_structured_motion(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["delta_theta_small_ok"] is True
    assert result["measured"]["tau_shape_ok"] is True
    assert result["measured"]["tau_inverse_ok"] is True
    assert result["measured"]["effect_structured_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_d2motionfromalphaport_check_reports_small_angle_shift(tmp_path):
    result = run_check(tmp_path)

    assert abs(result["measured"]["delta_theta_rad"]) < 2.0e-5
    assert result["samples"][0]["delta_tau"] < 0