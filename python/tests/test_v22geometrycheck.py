from __future__ import annotations

from pathlib import Path

from v22geometry_check import run_check


def test_v22geometry_check_reports_supported_geometry(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["geometrymodelok"] is True
    assert result["alpha0invarianttype"] in {"dimensionless_invariant", "dimensionless_shifted"}
    assert result["curvature_state"] == "flat-locally-stable"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()