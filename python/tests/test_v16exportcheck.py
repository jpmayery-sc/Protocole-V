from __future__ import annotations

from pathlib import Path

from v16export_check import run_check


def test_v16export_check_exports_the_prediction_package(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert set(result["measured"]["export_keys"]) == {"suite", "locked_names", "frozen_names", "internal", "external", "verdict"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()