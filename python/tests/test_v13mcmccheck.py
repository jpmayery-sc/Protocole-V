from __future__ import annotations

from pathlib import Path

from v13mcmc_check import run_check


def test_v13mcmc_check_produces_supported_posterior(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert 0.15 <= result["measured"]["acceptance_rate"] <= 0.85
    assert result["measured"]["samples_kept"] >= 200
    assert result["measured"]["map_supported"] is True
    assert result["measured"]["mean_supported"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()