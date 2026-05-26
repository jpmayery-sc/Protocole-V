from __future__ import annotations

from pathlib import Path

from v14sensi_check import run_check


def test_v14sensi_check_keeps_five_parameters(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["keep_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert result["measured"]["freeze_names"] == ["aE", "aR", "s_canal"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()