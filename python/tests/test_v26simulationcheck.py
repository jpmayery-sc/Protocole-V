from __future__ import annotations

from pathlib import Path

from v26simulation_check import run_check


def test_v26_simulation_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-SIMULATION"
    assert result["verdict"] == "supported"
    assert result["simulationgeometryok"] is True
    assert result["quantumsimulationok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
