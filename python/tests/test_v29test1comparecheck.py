from __future__ import annotations

from pathlib import Path

from v29test1_compare_check import run_check


def test_v29_test1_compare_check_reports_supported_or_partial(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-T1-DATA-COMPARISON"
    assert result["verdict"] in {"supported", "partial"}
    assert result["datasets"]["chronometers"]["rows"] == 32
    assert result["datasets"]["bao"]["rows"] == 12
    assert result["datasets"]["pantheon_plus_shoes"]["rows"] == 1701
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()