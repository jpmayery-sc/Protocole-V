from __future__ import annotations

from pathlib import Path

from run_experience4_global_suite import run_suite


def test_experience4_global_suite_includes_all_added_levels(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "partiel"
    assert result["supported_count"] == 9
    assert result["total"] == 11

    labels = {item["label"] for item in result["items"]}
    assert labels == {"atom_basics", "point_atome_protocol", "point_atome_master", "s_law_master", "alphaportsuite", "v6_d2_electron", "v7unifiedphysics_suite", "v47_baryons_suite", "v48_b_suite", "v48_neutrinos_suite", "v49_photon_suite"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_experience4_global_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()