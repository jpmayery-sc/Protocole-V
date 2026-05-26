from __future__ import annotations

from pathlib import Path

from v18recheck_check import run_check


def test_v18recheck_check_keeps_v16_and_v17_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["internal_ok"] is True
    assert result["measured"]["external_ok"] is True
    assert result["measured"]["comparison_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()