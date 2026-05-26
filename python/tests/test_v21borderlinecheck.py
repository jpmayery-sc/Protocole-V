from __future__ import annotations

from pathlib import Path

from v21borderline_check import run_check


def test_v21borderline_check_reports_localized_borderline(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["classification"] == "localement bon"
    assert result["supported_chain_length"] == 4
    assert result["fragile_layer"] == "none"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v21borderline_check_keeps_bottleneck_flag(tmp_path):
    result = run_check(tmp_path)

    assert result["bottleneck_flag"] is True
    assert result["recovery_margin"] == 1.0e-06