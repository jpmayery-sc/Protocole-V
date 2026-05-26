from __future__ import annotations

from pathlib import Path

from v25falsification_check import run_check


def test_v25_falsification_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V25-TESTS-FALSIFIABLES"
    assert result["verdict"] == "supported"
    assert result["interferometry_prediction"] is True
    assert result["geometricacceleration_prediction"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
