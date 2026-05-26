from __future__ import annotations

from pathlib import Path

from runv6suite import run_suite


def test_v6_suite_writes_summary(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "supported"
    assert result["supported_count"] == 2
    assert result["total"] == 2
    assert result["suite"] == "v6_d2_electron"
    labels = {item["label"] for item in result["items"]}
    assert labels == {"d2_motion_from_alpha_port", "electron_channel_from_alpha"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v6_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()