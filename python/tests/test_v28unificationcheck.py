from __future__ import annotations

from pathlib import Path

from v28unification_check import run_check


def test_v28_unification_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-UNIFICATION"
    assert result["verdict"] == "supported"
    assert result["unification_consistency"] is True
    assert result["unifiedequationset"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
