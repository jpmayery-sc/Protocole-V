from __future__ import annotations

from pathlib import Path

from alphatorsionorder_check import run_check


def test_alphatorsionorder_check_supports_controlled_decay(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["trend_ok"] is True
    assert result["controlled_decay_ok"] is True
    assert result["order_spread_ok"] is True
    assert result["measured"]["kappa_2"] > result["measured"]["kappa_3"] > result["measured"]["kappa_4"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_alphatorsionorder_check_reports_expected_ratios(tmp_path):
    result = run_check(tmp_path)

    assert 0.1 < result["measured"]["ratio3over2"] < 0.2
    assert 0.2 < result["measured"]["ratio4over3"] < 0.4