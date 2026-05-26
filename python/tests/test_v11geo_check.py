from __future__ import annotations

from pathlib import Path

from v11geo_check import run_check


def test_v11geo_check_supports_small_geometric_redshift(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["sign_ok"] is True
    assert result["measured"]["amplitude_ok"] is True
    assert result["measured"]["growth_ok"] is True
    assert result["measured"]["z_growth_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v11geo_check_increases_with_torsion(tmp_path):
    result = run_check(tmp_path)

    nominal = [case["environments"][1]["redshift"] for case in result["cases"]]
    assert nominal[0] < nominal[1] < nominal[2] < nominal[3]