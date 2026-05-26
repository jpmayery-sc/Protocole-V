from __future__ import annotations

from pathlib import Path

from v19map_check import run_check


def test_v19map_check_reports_supported_map(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["supported_ratio"] == 1.0
    assert result["total"] == 13
    assert len(result["axes"]) == 5
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v19map_check_flags_alpha0_as_locked_axis(tmp_path):
    result = run_check(tmp_path)

    alpha_axis = next(axis for axis in result["axes"] if axis["axis"] == "alpha0")
    assert alpha_axis["stability_state"] == "locked"
    assert alpha_axis["supported_count"] == 1