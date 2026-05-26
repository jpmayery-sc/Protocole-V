from __future__ import annotations

from pathlib import Path

from v8level_check import run_check


def test_v8level_check_supports_torsion_correction(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["monotone_ok"] is True
    assert result["measured"]["positive_ok"] is True
    assert result["measured"]["band_ok"] is True
    assert result["measured"]["fe_peak_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v8level_check_increases_with_z(tmp_path):
    result = run_check(tmp_path)

    energies = [sample["delta_energy"] for sample in result["level_samples"]]
    assert energies[0] < energies[1] < energies[2]
    assert all(1.0e-6 <= value <= 1.0e-3 for value in energies)