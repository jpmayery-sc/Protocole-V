from __future__ import annotations

from pathlib import Path

from runv22simulation_suite import run_suite


def test_v22simulation_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v22simulation_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 4
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v22_wigner", "v22_geometry_simulation", "v22_stability_simulation", "v22_verdict_simulation"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v22simulation_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir