from __future__ import annotations

from pathlib import Path

from v26qft_check import run_check


def test_v26_qft_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V26-QFT"
    assert result["verdict"] == "supported"
    assert result["qft_consistency"] is True
    assert result["canonicalquantizationok"] is True
    assert result["tubemodesquantized"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
