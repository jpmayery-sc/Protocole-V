from __future__ import annotations

from pathlib import Path

from v17compare_check import run_check


def test_v17compare_check_fits_v16_inside_reference_bounds(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["all_in_bounds"] is True
    assert result["measured"]["all_signs_ok"] is True
    assert result["measured"]["comparison_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()