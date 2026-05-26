from __future__ import annotations

from pathlib import Path

from v27multiscale_check import run_check


def test_v27_multiscale_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V27-MULTISCALE"
    assert result["verdict"] == "supported"
    assert result["quantumscalesimulation"] is True
    assert result["multiscalecouplingok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
