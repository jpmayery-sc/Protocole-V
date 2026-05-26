from __future__ import annotations

from pathlib import Path

from runv40effective_suite import run_suite


def test_v40_effective_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v40effective_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 4
    assert result["v40_global_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v40_lagrangian", "v40_projection", "v40_stability", "v40_synthesis"}

    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v40_effective_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()