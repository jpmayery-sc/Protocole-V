from __future__ import annotations

from pathlib import Path

from v20hierarchy_check import run_check


def test_v20hierarchy_check_reports_supported_ranking(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["dominant_parameter"] == "alpha0"
    assert set(result["metric_parameters"]) == {"s_geo", "s_atom"}
    assert result["torsion_parameter"] == "p"
    assert result["coupling_parameter"] == "A_kappa"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v20hierarchy_check_is_stable(tmp_path):
    result = run_check(tmp_path)

    assert result["stable_hierarchy"] is True
    assert len(result["hierarchy_ranking"]) == 5