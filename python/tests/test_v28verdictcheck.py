from __future__ import annotations

from pathlib import Path

from v28verdict_check import run_check


def test_v28_verdict_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-VERDICT"
    assert result["verdict"] == "supported"
    assert result["v28_verdict"] == "supported"
    assert result["next_step"] == "extend_to_V29"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
