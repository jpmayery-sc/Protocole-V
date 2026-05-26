from __future__ import annotations

from pathlib import Path

from v28renormmultiscale_check import run_check


def test_v28_renorm_multiscale_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V28-RENORMALISATION-MULTISCALE"
    assert result["verdict"] == "supported"
    assert result["renormalized_lagrangian"] is True
    assert result["multiscale_counterterms"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
