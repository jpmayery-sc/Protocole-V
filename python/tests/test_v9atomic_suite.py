from __future__ import annotations

from pathlib import Path

from runv9atomic_suite import run_suite


def test_v9atomic_suite_is_supported(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v9atomicsuite"
    assert result["total"] == 3
    assert result["supported_count"] == 3
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v9_crit", "v9_fine", "v9_map"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v9atomic_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()