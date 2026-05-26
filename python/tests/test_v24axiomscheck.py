from __future__ import annotations

from pathlib import Path

from v24axioms_check import run_check


def test_v24_axioms_check_reports_supported_axioms(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["axioms_consistency"] is True
    assert len(result["axioms_list"]) == 6
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()