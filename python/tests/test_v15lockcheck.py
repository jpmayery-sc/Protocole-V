from __future__ import annotations

from pathlib import Path

from v15lock_check import run_check


def test_v15lock_check_freezes_the_final_vector(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["locked_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert result["measured"]["frozen_names"] == ["aE", "aR", "s_canal"]
    assert result["measured"]["supported"] is True
    assert result["measured"]["alpha_repaired_ok"] is True
    assert result["measured"]["redshift_ok"] is True
    assert result["measured"]["fine_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()