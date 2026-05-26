from __future__ import annotations

from pathlib import Path

from v25cosmology_check import run_check


def test_v25_cosmology_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V25-COSMOLOGY"
    assert result["verdict"] == "supported"
    assert result["geometricaccelerationmodel"] is True
    assert result["k_vide_variation"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
