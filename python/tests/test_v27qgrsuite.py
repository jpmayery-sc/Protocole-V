from __future__ import annotations

from pathlib import Path

from runv27qgr_suite import run_suite


def test_v27_qgr_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v27qgr_suite"
    assert result["total"] == 6
    assert result["supported_count"] == 6
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v27_qgr", "v27_renormalisation", "v27_multiscale", "v27_observables_advanced", "v27_publication_advanced", "v27_verdict"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v27_qgr_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()