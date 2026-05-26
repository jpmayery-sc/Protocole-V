from __future__ import annotations

from pathlib import Path

from v23invariants_check import run_check


def test_v23_invariants_check_reports_stable_invariants(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["stable"] is True
    assert result["invariantsstabilitystate"] == "stable"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()