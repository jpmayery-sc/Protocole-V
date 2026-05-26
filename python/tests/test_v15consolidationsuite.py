from __future__ import annotations

from pathlib import Path

from runv15consolidation_suite import run_suite


def test_v15consolidation_suite_reports_supported_consolidation(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v15consolidation_suite"
    assert result["total"] == 3
    assert result["supported_count"] == 3
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v15_stability", "v15_robustness", "v15_lock"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v15consolidation_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir