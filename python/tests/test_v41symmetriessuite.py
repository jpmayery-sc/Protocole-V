from __future__ import annotations

from typing import cast
from pathlib import Path

from scripts.runv41symmetries_suite import run_suite


def test_v41_symmetry_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v41symmetries_suite"
    assert result["total"] == 6
    assert result["supported_count"] == 6
    assert result["v41_global_verdict"] == "supported"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v41_setup",
        "v41_continuous",
        "v41_discrete",
        "v41_geometric",
        "v41_conserved",
        "v41_synthesis",
    }

    assert Path(cast(str, result["json_path"])) .exists()
    assert Path(cast(str, result["txt_path"])) .exists()


def test_v41_symmetry_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])) .parent == expected_dir
    assert Path(cast(str, result["txt_path"])) .parent == expected_dir
    assert Path(cast(str, result["json_path"])) .exists()
    assert Path(cast(str, result["txt_path"])) .exists()