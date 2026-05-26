from __future__ import annotations

from pathlib import Path

from v15stability_check import run_check


def test_v15stability_check_keeps_the_locked_vector_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["locked_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert result["measured"]["frozen_names"] == ["aE", "aR", "s_canal"]
    assert result["measured"]["supported_cases"] == result["measured"]["total_cases"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()