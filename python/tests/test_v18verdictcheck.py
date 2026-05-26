from __future__ import annotations

from pathlib import Path

from v18verdict_check import run_check


def test_v18verdict_check_reports_supported_or_improved(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] in {"supported-improved", "supported-neutral"}
    assert result["measured"]["improved"] in {True, False}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()