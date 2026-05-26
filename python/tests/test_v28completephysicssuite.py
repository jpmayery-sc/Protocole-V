from __future__ import annotations

from pathlib import Path

from runv28completephysics_suite import run_suite


def test_v28_complete_physics_suite_reports_supported_pipeline(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v28completephysics_suite"
    assert result["total"] == 10
    assert result["supported_count"] == 10
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {
        "v28_unification",
        "v28_qgr_complete",
        "v28_renorm_multiscale",
        "v28_cosmology_full",
        "v28_tubes_full",
        "v28_intrication",
        "v28_simulation_hpc",
        "v28_observables_ultimes",
        "v28_article_latex",
        "v28_verdict",
    }
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v28_complete_physics_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()