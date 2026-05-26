from __future__ import annotations

from pathlib import Path

from v10ion_check import run_check


def test_v10ion_check_supports_critical_threshold(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["critical_peak_ok"] is True
    assert result["measured"]["decline_after_peak_ok"] is True
    assert result["measured"]["zcrit_band_ok"] is True
    assert result["measured"]["v9_coherence_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v10ion_check_places_zcrit_in_expected_band(tmp_path):
    result = run_check(tmp_path)

    assert 25 <= result["measured"]["peak_z"] <= 27
    assert 30 <= result["measured"]["z_ion_crit"] <= 40