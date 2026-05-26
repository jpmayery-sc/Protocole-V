from __future__ import annotations

from pathlib import Path

from v26observables_check import run_check


def test_v26_observables_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-OBSERVABLES"
    assert result["verdict"] == "supported"
    assert result["geometric_observables"]
    assert result["quantum_observables"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
