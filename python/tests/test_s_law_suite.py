from __future__ import annotations

from pathlib import Path

from run_s_law_suite import run_suite


def test_s_law_suite_includes_point_atome_master(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "partiel"
    assert result["support_total"] == 11
    assert result["falsifier_total"] == 2
    assert result["total"] == 13

    labels = {item["label"] for item in result["items"]}
    assert "point_atome_master" in labels
    assert "heavy_border" in labels
    assert "alphaportsuite" in labels
    assert "v6_d2_electron" in labels
    assert "v7unifiedphysics_suite" in labels
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_s_law_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()