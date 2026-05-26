from __future__ import annotations

from pathlib import Path

from v26verdict_check import run_check


def test_v26_verdict_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-VERDICT"
    assert result["verdict"] == "supported"
    assert result["v26_verdict"] == "supported"
    assert result["next_step"] == "extend_to_V27"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
