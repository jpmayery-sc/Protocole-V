from __future__ import annotations

from pathlib import Path

from runv12falsifiersuite import run_suite


def test_v12falsifier_suite_reports_falsification(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v12falsifier_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 2
    assert result["falsified_count"] == 2
    assert result["overall_verdict"] == "falsified"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v12_absolute", "v12_alpha", "v12_fine", "v12_global"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v12falsifier_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()