from __future__ import annotations

from pathlib import Path

from v28cosmologyfull_check import run_check


def test_v28_cosmology_full_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-COSMOLOGY-FULL"
    assert result["verdict"] == "supported"
    assert result["intricationenergyterm"] is True
    assert result["accelerationwithoutdark_energy"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
