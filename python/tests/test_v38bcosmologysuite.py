from __future__ import annotations

from pathlib import Path

from runv38bcosmo_suite import run_suite


def test_v38b_cosmology_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v38bcosmo_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 4
    assert result["v38b_global_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v38b_hubble", "v38b_lambda", "v38b_growth", "v38b_tester_summary"}

    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v38b_cosmology_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()