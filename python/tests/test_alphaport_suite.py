from __future__ import annotations

from pathlib import Path

from runalphaport_suite import run_suite


def test_alphaport_suite_writes_summary(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "supported"
    assert result["supported_count"] == 3
    assert result["total"] == 3
    assert result["suite"] == "alphaportsuite"
    assert [item["label"] for item in result["items"]] == [
        "alphaenergyrunning",
        "alphatorsionorder",
        "alphageometricport",
    ]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_alphaport_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()