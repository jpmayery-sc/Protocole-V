from __future__ import annotations

from pathlib import Path

from electronchannelfromalphacheck import run_check


def test_electronchannelfromalphacheck_supports_power_law_channel(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["decreasing_ok"] is True
    assert result["exponent_ok"] is True
    assert result["fit_quality_ok"] is True
    assert result["channel_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_electronchannelfromalphacheck_reports_strong_decay_exponent(tmp_path):
    result = run_check(tmp_path)

    assert result["measured"]["exponent"] > 4.0
    assert result["measured"]["relative_rmse"] < 0.15