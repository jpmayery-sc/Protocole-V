from __future__ import annotations

from pathlib import Path

from run_atom_basics_suite import run_suite


def test_atom_basics_suite_includes_nzstability(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "supported"
    assert result["supported_count"] == 4
    assert result["total"] == 4

    labels = {item["label"] for item in result["items"]}
    assert labels == {"neutral_atom", "iron_rust", "h_fe_pb", "nzstability"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_atom_basics_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "python" / "results" / "atom_basics"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()