from __future__ import annotations

from pathlib import Path
from typing import cast

from scripts.runv42quantum_suite import run_suite


def test_v42_quantum_suite_reports_supported_pipeline(tmp_path):
    result = cast(dict[str, object], run_suite(tmp_path))

    assert result["suite"] == "v42quantum_suite"
    assert result["total"] == 6
    assert result["supported_count"] == 6
    assert result["v42_global_verdict"] == "supported"

    items = cast(list[dict[str, object]], result["items"])
    labels = {cast(str, item["label"]) for item in items}
    assert labels == {
        "v42_fields",
        "v42_propagators",
        "v42_interactions",
        "v42_loops",
        "v42_renormality",
        "v42_synthesis",
    }

    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()


def test_v42_quantum_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = cast(dict[str, object], run_suite())

    expected_dir = root / "results" / "result-analyse"
    assert Path(cast(str, result["json_path"])).parent == expected_dir
    assert Path(cast(str, result["txt_path"])).parent == expected_dir
    assert Path(cast(str, result["json_path"])).exists()
    assert Path(cast(str, result["txt_path"])).exists()