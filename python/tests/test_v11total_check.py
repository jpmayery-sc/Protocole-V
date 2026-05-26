from __future__ import annotations

from pathlib import Path

from v11total_check import run_check


def test_v11total_check_supports_combined_redshift(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["nominal_band_ok"] is True
    assert result["measured"]["z_order_ok"] is True
    assert result["measured"]["env_order_ok"] is True
    assert result["measured"]["testable_window_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v11total_check_produces_small_nominal_values(tmp_path):
    result = run_check(tmp_path)

    nominal = [case["nominal_z_mod"] for case in result["cases"]]
    assert all(1.0e-6 <= value <= 1.0e-5 for value in nominal)
    assert nominal[0] < nominal[1] < nominal[2] < nominal[3]