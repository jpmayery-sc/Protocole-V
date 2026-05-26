from __future__ import annotations

from pathlib import Path
from typing import cast

from scripts.runv43predictions_suite import run_suite


def test_v43_predictions_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v43predictions_suite"
    assert result["total"] == 5
    assert result["supported_count"] == 5
    assert result["v43_global_verdict"] == "supported"
    assert "external_references" in result

    external_references = cast(dict[str, dict[str, str]], result["external_references"])
    assert external_references["muon_g2"]["value"] == "a_mu(Exp) = 116592059(22) x 10^-11"
    assert external_references["kids_1000"]["observable"] == "S8"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v43_colliders",
        "v43_flavour",
        "v43_cosmology",
        "v43_astro",
        "v43_synthesis",
    }

    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()


def test_v43_predictions_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])).parent == expected_dir
    assert Path(cast(str, result["txt_path"])).parent == expected_dir
    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()