from __future__ import annotations

from pathlib import Path

from v10spectre_check import run_check


def test_v10spectre_check_supports_torsion_series(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["series_monotone_ok"] is True
    assert result["measured"]["band_ok"] is True
    assert result["measured"]["z_growth_ok"] is True
    assert result["measured"]["v9_coherence_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v10spectre_check_corrections_increase_with_z(tmp_path):
    result = run_check(tmp_path)

    corrections_at_n2 = [entry["correction_at_n2"] for entry in result["series"]]
    assert corrections_at_n2[0] < corrections_at_n2[1] < corrections_at_n2[2] < corrections_at_n2[3] < corrections_at_n2[4]