from __future__ import annotations

from pathlib import Path

from runv11redshiftsuite import run_suite


def test_v11redshift_suite_is_supported(tmp_path):
    result = run_suite(tmp_path)

    assert result["suite"] == "v11redshift_suite"
    assert result["total"] == 4
    assert result["supported_count"] == 4
    assert result["overall_verdict"] == "supported"

    labels = {item["label"] for item in result["items"]}
    assert labels == {"v11_geo", "v11_atom", "v11_canal", "v11_total"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v11redshift_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    result = run_suite()

    expected_dir = root / "results" / "result-analyse"
    assert Path(result["json_path"]).parent == expected_dir
    assert Path(result["txt_path"]).parent == expected_dir
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()