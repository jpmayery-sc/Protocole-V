from __future__ import annotations

from pathlib import Path

from v12absolute_check import run_check


def test_v12absolute_check_supports_conservative_bounds(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["geo"]["in_bounds"] is True
    assert result["measured"]["atom"]["in_bounds"] is True
    assert result["measured"]["canal"]["in_bounds"] is True
    assert result["measured"]["total"]["in_bounds"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v12absolute_check_keeps_geo_order(tmp_path):
    result = run_check(tmp_path)

    assert result["measured"]["geo"]["monotone_ok"] is True