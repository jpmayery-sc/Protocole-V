from __future__ import annotations

from pathlib import Path

from v14reduce_check import run_check


def test_v14reduce_check_preserves_calibration_with_reduced_vector(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["reduction_ratio"] == 0.625
    assert result["measured"]["supported"] is True
    assert result["measured"]["alpha_repaired_ok"] is True
    assert result["measured"]["redshift_ok"] is True
    assert result["measured"]["fine_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()