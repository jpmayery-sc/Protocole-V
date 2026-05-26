from __future__ import annotations

from pathlib import Path

from v29observationaltests_check import run_check


def test_v29_observational_tests_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-OBSERVATIONAL-TESTS"
    assert result["verdict"] == "supported"
    assert result["lcdmfalsificationtests"] is True
    assert result["predicted_signatures"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
