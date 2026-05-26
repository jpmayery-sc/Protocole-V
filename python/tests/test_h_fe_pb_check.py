from __future__ import annotations

from pathlib import Path

from h_fe_pb_check import run_check


def test_h_fe_pb_check_supports_v4_nuclear_stability_curve(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["curve_ok"] is True
    assert result["shape"] == "cloche"
    assert result["peak_case"]["name"] == "Fe-56"
    assert result["light_side_ok"] is True
    assert result["heavy_side_ok"] is True
    assert result["rising_branch_ok"] is True
    assert result["falling_branch_ok"] is True
    assert len(result["cases"]) == 7
    assert result["ordered_case_names"] == ["H-1", "He-4", "C-12", "O-16", "Fe-56", "Pb-208", "U-238"]
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_h_fe_pb_check_reports_the_expected_peak_energy(tmp_path):
    result = run_check(tmp_path)

    assert 8.7 < result["peak_energy"] < 8.9
    assert result["case_control"] == "H-1 -> He-4 -> C-12 -> O-16 -> Fe-56 -> Pb-208 -> U-238"