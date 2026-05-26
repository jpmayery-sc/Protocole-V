from __future__ import annotations

from pathlib import Path

from v12global_check import run_check


def test_v12global_check_marks_model_falsified(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "falsified"
    assert result["measured"]["falsified_count"] == 1
    assert result["measured"]["supported_count"] == 2
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v12global_check_tracks_alpha_falsification(tmp_path):
    result = run_check(tmp_path)

    verdicts = {item["label"]: item["verdict"] for item in result["items"]}
    assert verdicts["v12_alpha"] == "falsifie"