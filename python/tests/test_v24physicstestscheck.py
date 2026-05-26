from __future__ import annotations

from pathlib import Path

from v24physicstests_check import run_check


def test_v24_physics_tests_check_reports_passed_tests(tmp_path):
    result = run_check(tmp_path)

    assert result["physics_verdict"] == "supported"
    assert result["physicstestspassed"] is True
    assert result["failed_tests"] == []
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()