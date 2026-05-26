from __future__ import annotations

from pathlib import Path

from v23verdict_check import run_check


def test_v23_verdict_check_reports_coherent_model(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["v23verdict"] == "coherent_model"
    assert result["confidence_level"] == "very_high"
    assert result["coherent_model"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()