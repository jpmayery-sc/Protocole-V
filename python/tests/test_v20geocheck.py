from __future__ import annotations

from pathlib import Path

from v20geo_check import run_check


def test_v20geo_check_reports_supported_geostructure(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["geostructureok"] is True
    assert result["metric_consistency"] is True
    assert result["alpha0_geometriclink"] > 0.0
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v20geo_check_keeps_curvature_bounded(tmp_path):
    result = run_check(tmp_path)

    assert result["curvature_indicator"] <= 1.0e-4