from __future__ import annotations

from pathlib import Path

from v29theoryfinal_check import run_check


def test_v29_theory_final_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V29-THEORY-FINAL"
    assert result["verdict"] == "supported"
    assert result["final_consistency"] is True
    assert result["final_invariants"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
