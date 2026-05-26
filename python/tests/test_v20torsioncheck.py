from __future__ import annotations

from pathlib import Path

from v20torsion_check import run_check


def test_v20torsion_check_reports_supported_torsion(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["torsion_stability"] is True
    assert result["torsion_strength"] > 0.0
    assert result["torsion_kappa_coupling"] > 0.0
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v20torsion_check_shows_affine_signature(tmp_path):
    result = run_check(tmp_path)

    assert result["affine_signature"]["p"] in {"positive", "negative"}
    assert result["affine_signature"]["A_kappa"] in {"positive", "negative"}