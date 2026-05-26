from __future__ import annotations

from pathlib import Path

from v25quantum_check import run_check


def test_v25_quantum_check_reports_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["section"] == "V25-QUANTUM"
    assert result["verdict"] == "supported"
    assert result["quantization_consistency"] is True
    assert result["spinquantizationok"] is True
    assert result["variationnalquantizationok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()
