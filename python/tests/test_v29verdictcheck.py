from __future__ import annotations

from pathlib import Path

from v29verdict_check import run_check


def test_v29_verdict_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-VERDICT"
    assert result["verdict"] == "supported"
    assert result["v29_verdict"] == "supported"
    assert result["next_step"] == "extend_to_V30"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
