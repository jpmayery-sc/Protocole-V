from __future__ import annotations

from pathlib import Path
from typing import cast

from scripts.runv48neutrinos_suite import run_suite


def test_v48_neutrinos_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v48neutrinos_suite"
    assert result["total"] == 6
    assert result["supported_count"] == 6
    assert result["v48_global_verdict"] == "supported"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v48_mass_model",
        "v48_mixing",
        "v48_sterile_dynamics",
        "v48_cosmo_constraints",
        "v48_decays",
        "v48_synthesis",
    }

    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()


def test_v48_neutrinos_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])).parent == expected_dir
    assert Path(cast(str, result["txt_path"])).parent == expected_dir
    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()