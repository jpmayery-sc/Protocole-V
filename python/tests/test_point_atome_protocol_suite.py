from __future__ import annotations

from pathlib import Path

from run_point_atome_protocol_suite import run_suite


def test_point_atome_protocol_suite_includes_atom_basics(tmp_path):
    result = run_suite(tmp_path)

    assert result["total"] == 5
    assert result["supported_count"] == 5
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"saturation_magnetic", "omega_structure", "heavy_border", "atom_basics", "regime_physics"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_point_atome_protocol_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()