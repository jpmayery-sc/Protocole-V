from __future__ import annotations

from pathlib import Path

from v22torsion_theory_check import run_check


def test_v22torsion_theory_check_reports_supported_torsion(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["torsionmodelok"] is True
    assert result["torsionstabilitystate"] == "stable"
    assert result["torsioninvarianttype"] == "metric_affine_with_torsion"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()