from __future__ import annotations

from pathlib import Path

from v24lagrangian_check import run_check


def test_v24_lagrangian_check_reports_supported_lagrangian(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["lagrangian_consistency"] is True
    assert "L_tot" in result["lagrangian_form"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()