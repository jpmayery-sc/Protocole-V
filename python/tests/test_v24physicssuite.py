from __future__ import annotations

from pathlib import Path

from runv24physics_suite import run_suite


def test_v24_physics_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v24physics_suite"
    assert result["total"] == 5
    assert result["supported_count"] == 5
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v24_axioms", "v24_lagrangian", "v24_effectivephysics", "v24_physicstests", "v24_verdict"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v24_physics_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir