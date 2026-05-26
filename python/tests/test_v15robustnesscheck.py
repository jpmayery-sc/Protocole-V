from __future__ import annotations

from pathlib import Path

from v15robustness_check import run_check


def test_v15robustness_check_preserves_the_expected_trends(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["locked_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert result["measured"]["supported_rows"] == result["measured"]["total_rows"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()