from __future__ import annotations

from pathlib import Path

from v11atom_check import run_check


def test_v11atom_check_supports_internal_redshift(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["amplitude_ok"] is True
    assert result["measured"]["z_growth_ok"] is True
    assert result["measured"]["env_growth_ok"] is True
    assert result["measured"]["heavy_tail_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v11atom_check_grows_with_z(tmp_path):
    result = run_check(tmp_path)

    nominal = [case["nominal_redshift"] for case in result["cases"]]
    assert nominal[0] < nominal[1] < nominal[2] < nominal[3] < nominal[4]