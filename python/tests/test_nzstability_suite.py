from __future__ import annotations

from pathlib import Path

from run_nzstability_suite import run_suite


def test_nzstability_suite_writes_summary(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "supported"
    assert result["supported_count"] == 1
    assert result["total"] == 1
    assert result["suite"] == "nzstability"
    assert result["items"][0]["label"] == "nzstability"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_nzstability_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "python" / "results" / "nzstability"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()