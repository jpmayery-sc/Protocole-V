from __future__ import annotations

from pathlib import Path

from v28intrication_check import run_check


def test_v28_intrication_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-INTRICATION-FONDAMENTALE"
    assert result["verdict"] == "supported"
    assert result["intricationgeometrymap"] is True
    assert result["intricationoperatorset"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
