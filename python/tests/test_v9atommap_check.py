from __future__ import annotations

from pathlib import Path

from v9atommap_check import run_check


def test_v9atommap_check_supports_reduced_atomic_map(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["radius_monotone_ok"] is True
    assert result["measured"]["level_monotone_ok"] is True
    assert result["measured"]["stability_peak_ok"] is True
    assert result["measured"]["heavy_limit_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v9atommap_check_peak_is_fe(tmp_path):
    result = run_check(tmp_path)

    rows = result["rows"]
    scores = {row["symbol"]: row["stability_score"] for row in rows}
    assert scores["Fe"] == max(scores.values())
    assert scores["Pb"] < scores["Fe"]
    assert scores["U"] < scores["Pb"]