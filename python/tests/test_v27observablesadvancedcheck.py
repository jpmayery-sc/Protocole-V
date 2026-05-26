from __future__ import annotations

from pathlib import Path

from v27observablesadvanced_check import run_check


def test_v27_observables_advanced_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V27-OBSERVABLES-AVANCÉS"
    assert result["verdict"] == "supported"
    assert result["advancedquantumobservables"] is True
    assert result["advancedgeometricobservables"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
