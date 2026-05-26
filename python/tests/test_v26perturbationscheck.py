from __future__ import annotations

from pathlib import Path

from v26perturbations_check import run_check


def test_v26_perturbations_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-PERTURBATIONS"
    assert result["verdict"] == "supported"
    assert result["perturbation_stability"] is True
    assert result["tubeperturbationspectrum"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
