from __future__ import annotations

from pathlib import Path

from v13params_check import run_check


def test_v13params_check_supports_theta_support_region(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["bounds_ok"] is True
    assert result["measured"]["target_ok"] is True
    assert result["measured"]["order_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()