from __future__ import annotations

from pathlib import Path

from v16internal_check import run_check


def test_v16internal_check_produces_internal_predictions(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["theta_supported"] is True
    assert result["internal"]["alpha_residual"] < 1.0e-8
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()