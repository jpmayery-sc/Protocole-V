from __future__ import annotations

from pathlib import Path

from v23domain_check import run_check


def test_v23_domain_check_reports_bounded_domain(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["safe_region"]["label"] == "safe"
    assert result["borderline_region"]["label"] == "borderline"
    assert result["forbidden_region"]["label"] == "forbidden"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()