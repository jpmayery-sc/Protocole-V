from __future__ import annotations

from pathlib import Path

from v19robustglobal_check import run_check


def test_v19robustglobal_check_reports_borderline_robustness(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "borderline"
    assert result["supported_chain_length"] == 4
    assert result["fragile_layer"] == "none"
    assert result["bottleneck_flag"] is True
    assert result["recovery_margin"] < 0.002
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v19robustglobal_check_uses_v18_neighborhood(tmp_path):
    result = run_check(tmp_path)

    map_verdicts = [axis["verdict"] for axis in result["map"]["axes"]]
    assert map_verdicts.count("supported") >= 1