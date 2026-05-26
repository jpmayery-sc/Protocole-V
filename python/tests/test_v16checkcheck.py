from __future__ import annotations

from pathlib import Path

from v16check_check import run_check


def test_v16check_check_confirms_internal_external_consistency(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["internal_ok"] is True
    assert result["measured"]["external_ok"] is True
    assert result["measured"]["consistency_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()