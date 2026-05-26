from __future__ import annotations

from pathlib import Path

from v12fine_check import run_check


def test_v12fine_check_supports_fine_bounds(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["absolute_band_ok"] is True
    assert result["measured"]["monotone_ok"] is True
    assert result["measured"]["fe_stable_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v12fine_check_keeps_u_above_fe(tmp_path):
    result = run_check(tmp_path)

    values = {case["name"]: case["correction"] for case in result["cases"]}
    assert values["Fe"] < values["Xe"] < values["Pb"] < values["U"]