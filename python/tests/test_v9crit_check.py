from __future__ import annotations

from pathlib import Path

from v9crit_check import run_check


def test_v9crit_check_supports_critical_regime(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["critical_peak_ok"] is True
    assert result["measured"]["decline_after_peak_ok"] is True
    assert result["measured"]["heavy_tail_ok"] is True
    assert result["measured"]["zcrit_band_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v9crit_check_places_peak_near_fe(tmp_path):
    result = run_check(tmp_path)

    assert 24 <= result["measured"]["peak_z"] <= 26
    assert 30 <= result["measured"]["z_crit"] <= 40