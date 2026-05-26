from __future__ import annotations

from pathlib import Path

from v7geo_check import run_check


def test_v7geo_check_supports_monotone_trajectories(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["trajectory_monotone_ok"] is True
    assert result["measured"]["precession_monotone_ok"] is True
    assert result["measured"]["precession_positive_ok"] is True
    assert result["measured"]["radial_monotone_ok"] is True
    assert result["measured"]["radial_small_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v7geo_check_reports_increasing_precession(tmp_path):
    result = run_check(tmp_path)

    precession_values = [sample["precession_rad"] for sample in result["samples"]]
    assert precession_values[0] < precession_values[-1]
    assert result["samples"][0]["theta_track"] < result["samples"][-1]["theta_track"]