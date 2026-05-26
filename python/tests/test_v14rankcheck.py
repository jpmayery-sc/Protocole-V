from __future__ import annotations

from pathlib import Path

from v14rank_check import run_check


def test_v14rank_check_prioritizes_alpha_geo_atom_and_corrections(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["keep_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert set(result["measured"]["strong"]) == {"alpha0", "s_geo", "s_atom"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()