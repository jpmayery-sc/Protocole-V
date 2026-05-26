from __future__ import annotations

from pathlib import Path

from v24verdict_check import run_check


def test_v24_verdict_check_reports_supported_v24(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["v24_verdict"] == "supported"
    assert result["next_step"] == "extend_to_V25"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()