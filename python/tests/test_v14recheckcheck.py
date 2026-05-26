from __future__ import annotations

from pathlib import Path

from v14recheck_check import run_check


def test_v14recheck_check_keeps_the_chain_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["v11_ok"] is True
    assert result["measured"]["v12_ok"] is True
    assert result["measured"]["v13_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()