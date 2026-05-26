from __future__ import annotations

from pathlib import Path

from v27qgr_check import run_check


def test_v27_qgr_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V27-QGR"
    assert result["verdict"] == "supported"
    assert result["qgr_consistency"] is True
    assert result["relativisticpropagationok"] is True
    assert result["relativistictubemodes"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
