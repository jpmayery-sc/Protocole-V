from __future__ import annotations

from pathlib import Path

from v17verdict_check import run_check


def test_v17verdict_check_returns_supported_verdict(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["verdict"] == "supported"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()