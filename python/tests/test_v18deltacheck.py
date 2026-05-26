from __future__ import annotations

from pathlib import Path

from v18delta_check import run_check


def test_v18delta_check_reports_supported_baseline(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["deviation_class"] == "supported"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()