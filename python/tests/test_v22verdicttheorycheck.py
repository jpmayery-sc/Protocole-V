from __future__ import annotations

from pathlib import Path

from v22verdict_theory_check import run_check


def test_v22verdict_theory_check_reports_coherent_theory(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["theory_verdict"] == "coherent_theory"
    assert result["open_questions"] == []
    assert result["V22_GEOMETRY"]["geometrymodelok"] is True
    assert result["V22_TORSION_THEORY"]["torsionmodelok"] is True
    assert result["V22_HIERARCHY_THEORY"]["hierarchymodelok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()