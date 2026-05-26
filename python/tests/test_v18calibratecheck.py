from __future__ import annotations

from pathlib import Path

from v18calibrate_check import run_check


def test_v18calibrate_check_runs_three_profiles(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] in {"supported-improved", "supported-neutral"}
    assert result["measured"]["profile_count"] == 3
    assert result["measured"]["supported_profiles"] == 3
    assert result["measured"]["best_profile"] in {"calibration_douce", "calibration_standard", "calibration_agressive"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()