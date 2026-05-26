from __future__ import annotations

from pathlib import Path

from v13likelihood_check import run_check


def test_v13likelihood_check_prefers_the_calibrated_solution(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["alpha_repaired_ok"] is True
    assert result["measured"]["target_better_ok"] is True
    assert result["measured"]["finite_ok"] is True
    assert result["measured"]["target_log_likelihood"] > result["measured"]["perturbed_log_likelihood"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()