from __future__ import annotations

from pathlib import Path

from v29hpcsimulation_check import run_check


def test_v29_hpc_simulation_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-HPC-SIMULATION"
    assert result["verdict"] == "supported"
    assert result["hpcquantumoutput"] is True
    assert result["hpcmultiscalemap"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
