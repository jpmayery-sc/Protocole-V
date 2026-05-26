from __future__ import annotations

from pathlib import Path

from v25spintorsion_check import run_check


def test_v25_spin_torsion_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V25-SPIN-TORSION"
    assert result["verdict"] == "supported"
    assert result["spintopologyclassification"] is True
    assert result["bosonfermionsplit"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
