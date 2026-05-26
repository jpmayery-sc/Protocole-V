from __future__ import annotations

from pathlib import Path

from runv14reduction_suite import run_suite


def test_v14reduction_suite_reports_supported_reduction(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v14reduction_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 4
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v14_sensi", "v14_rank", "v14_reduce", "v14_recheck"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v14reduction_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir