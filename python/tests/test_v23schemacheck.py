from __future__ import annotations

from pathlib import Path

from v23schema_check import run_check


def test_v23_schema_check_reports_supported_schema(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["schema_ok"] is True
    assert result["schema_consistency"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()