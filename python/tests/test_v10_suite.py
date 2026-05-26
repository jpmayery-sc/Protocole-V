from __future__ import annotations

from pathlib import Path

import pytest

from v10_bridge import build_v10_bridge
from run_v10_suite import run_suite


pytestmark = pytest.mark.flow


def test_v10_suite_writes_summary(tmp_path):
    result = run_suite(tmp_path)

    assert result["overall_verdict"] == "supported"
    assert result["supported_count"] == 4
    assert result["total"] == 4
    assert result["manifest_status"] == "partial"
    assert result["bridge_ready_count"] == 4

    labels = {item["label"] for item in result["items"]}
    assert labels == {"zenodo-7313581", "zenodo-7631438", "zenodo-10605186", "zenodo-5001776"}
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v10_suite_matches_bridge_inventory():
    root = Path(__file__).resolve().parents[2]
    suite_result = run_suite()
    bridge = build_v10_bridge(root)

    suite_labels = {item["label"] for item in suite_result["items"]}
    bridge_ids = {row["source_id"] for row in bridge["rows"]}

    assert suite_result["supported_count"] == bridge["bridge_ready_count"] == 4
    assert suite_result["total"] == bridge["source_count"] == 4
    assert suite_labels == bridge_ids
    assert suite_result["manifest_status"] == bridge["manifest_status"] == "partial"


def test_v10_suite_defaults_to_workspace_results_dir():
    root = Path(__file__).resolve().parents[2]
    suite_result = run_suite()

    expected_dir = root / "python" / "results" / "v10"
    assert Path(suite_result["json_path"]).parent == expected_dir
    assert Path(suite_result["txt_path"]).parent == expected_dir
    assert Path(suite_result["json_path"]).exists()
    assert Path(suite_result["txt_path"]).exists()
