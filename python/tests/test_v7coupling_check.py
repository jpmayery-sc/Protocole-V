from __future__ import annotations

from pathlib import Path

from v7coupling_check import run_check


def test_v7coupling_check_supports_dynamic_field(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["domain_ok"] is True
    assert result["measured"]["partial_E_positive_ok"] is True
    assert result["measured"]["partial_n_negative_ok"] is True
    assert result["measured"]["partial_r_negative_ok"] is True
    assert result["measured"]["stability_surface_ok"] is True
    assert result["measured"]["stability_band_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v7coupling_check_reports_small_stability_range(tmp_path):
    result = run_check(tmp_path)

    assert result["measured"]["stability_range"] < 1.0e-4
    assert result["measured"]["alpha0"] > 0.0