from __future__ import annotations

from pathlib import Path

from v13postcheck_check import run_check


def test_v13postcheck_check_repairs_v12_alpha(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["alpha_repaired_ok"] is True
    assert result["measured"]["redshift_ok"] is True
    assert result["measured"]["fine_ok"] is True
    assert result["measured"]["theta_supported"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()