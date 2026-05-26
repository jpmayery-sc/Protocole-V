from __future__ import annotations

from pathlib import Path

from v28simulationhpc_check import run_check


def test_v28_simulation_hpc_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-SIMULATION-HPC"
    assert result["verdict"] == "supported"
    assert result["hpcsimulationok"] is True
    assert result["multiscalehpcoutput"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
