from __future__ import annotations

from pathlib import Path

from v22hierarchy_theory_check import run_check


def test_v22hierarchy_theory_check_reports_supported_hierarchy(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["hierarchymodelok"] is True
    assert result["hierarchystabilitystate"] == "stable"
    assert result["role_assignment"]["alpha0"] == "invariant"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()