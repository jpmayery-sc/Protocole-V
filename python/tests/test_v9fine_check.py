from __future__ import annotations

from pathlib import Path

from v9fine_check import run_check


def test_v9fine_check_supports_extreme_corrections(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["monotone_ok"] is True
    assert result["measured"]["band_ok"] is True
    assert result["measured"]["high_sensitivity_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v9fine_check_increases_with_z(tmp_path):
    result = run_check(tmp_path)

    energies = [sample["delta_energy"] for sample in result["samples"]]
    assert energies[0] < energies[1] < energies[2] < energies[3]