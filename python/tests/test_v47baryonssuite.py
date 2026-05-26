from __future__ import annotations

from pathlib import Path
from typing import cast

from scripts.runv47baryons_suite import run_suite


def test_v47_baryons_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v47baryons_suite"
    assert result["total"] == 6
    assert result["supported_count"] == 6
    assert result["v47_global_verdict"] == "supported"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v47_qcd_masses",
        "v47_qcd_splittings",
        "v47_beta_decays",
        "v47_nuclear_binding",
        "v47_stability",
        "v47_synthesis",
    }

    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()


def test_v47_baryons_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])).parent == expected_dir
    assert Path(cast(str, result["txt_path"])).parent == expected_dir
    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()