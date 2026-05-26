from __future__ import annotations

from pathlib import Path

from v10rydberg_check import run_check


def test_v10rydberg_check_supports_controlled_amplification(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["increasing_ok"] is True
    assert result["measured"]["band_ok"] is True
    assert result["measured"]["coherence_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v10rydberg_check_deviation_grows_with_n(tmp_path):
    result = run_check(tmp_path)

    deltas = [sample["delta_rn"] for sample in result["samples"]]
    assert deltas[0] < deltas[1] < deltas[2] < deltas[3] < deltas[4] < deltas[5]