from __future__ import annotations

from pathlib import Path

from v28observablesultimate_check import run_check


def test_v28_observables_ultimate_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-OBSERVABLES-ULTIMES"
    assert result["verdict"] == "supported"
    assert result["ultimateobservableslist"] is True
    assert result["observablepredictionset"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
