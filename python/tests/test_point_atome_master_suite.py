from __future__ import annotations

from pathlib import Path

from run_point_atome_master_suite import run_suite


def test_point_atome_master_suite_includes_atom_basics(tmp_path):
    result = run_suite(tmp_path)

    assert result["total"] == 22
    assert result["supported_count"] == 20
    assert result["overall_verdict"] == "partiel"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"point_atome_protocol", "atom_basics", "v8atomicsuite", "v9atomicsuite", "v10atomdynamics_suite", "v11redshift_suite", "v12falsifier_suite", "v13mcmc_suite", "v14reduction_suite", "v15consolidation_suite", "v16prediction_suite", "v17validation_suite", "v18calibration_suite", "v19metacalibration_suite", "v20research_suite", "v21borderline_suite", "v22theory_suite", "v22experiment_suite", "v22simulation_suite", "d1d4", "electron5_core", "electron5_extended"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_point_atome_master_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()