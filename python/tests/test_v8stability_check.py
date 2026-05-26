from __future__ import annotations

from pathlib import Path

from v8stability_check import run_check


def test_v8stability_check_supports_atomic_frontier(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["monotone_ok"] is True
    assert result["measured"]["fe_peak_ok"] is True
    assert result["measured"]["pb_decline_ok"] is True
    assert result["measured"]["positive_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v8stability_check_peaks_at_fe(tmp_path):
    result = run_check(tmp_path)

    scores = [sample["score"] for sample in result["stability_samples"]]
    assert scores[0] < scores[1] < scores[2]
    assert scores[3] < scores[2]