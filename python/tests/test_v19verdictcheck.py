from __future__ import annotations

from pathlib import Path

from v19verdict_check import run_check


def test_v19verdict_check_reports_local_pipeline_strength(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "partiel"
    assert result["classification"] == "localement bon"
    assert result["map"]["verdict"] == "supported"
    assert result["sensitivity"]["verdict"] == "supported"
    assert result["robust_global"]["verdict"] == "borderline"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()