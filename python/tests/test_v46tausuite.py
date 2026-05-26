from __future__ import annotations

from pathlib import Path
from typing import cast

from scripts.runv46tau_suite import run_suite


def test_v46_tau_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v46tau_suite"
    assert result["total"] == 5
    assert result["supported_count"] == 5
    assert result["v46_global_verdict"] == "supported"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v46_tau_gminus2",
        "v46_tau_decays",
        "v46_tau_lfu",
        "v46_tau_stability",
        "v46_synthesis",
    }

    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()


def test_v46_tau_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])).parent == expected_dir
    assert Path(cast(str, result["txt_path"])).parent == expected_dir
    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()