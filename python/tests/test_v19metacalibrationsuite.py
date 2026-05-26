from __future__ import annotations

from pathlib import Path

from runv19metacalibration_suite import run_suite


def test_v19metacalibration_suite_reports_partiel_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v19metacalibration_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 2
    assert result["overall_verdict"] == "partiel"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v19_map", "v19_sensitivity", "v19_robust_global", "v19_verdict"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v19metacalibration_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir