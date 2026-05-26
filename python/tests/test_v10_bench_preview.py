from __future__ import annotations

from pathlib import Path

import pytest

from v10_bridge import build_v10_bench_preview


pytestmark = pytest.mark.flow


def test_v10_bench_preview_stays_blocked_without_trials():
    root = Path(__file__).resolve().parents[2]
    preview = build_v10_bench_preview(root)

    assert preview["overall_verdict"] == "blocked"
    assert preview["input_status"] == "metadata_only"
    assert preview["source_count"] == 4
    assert preview["bridge_ready_count"] == 4
    assert preview["materials"] == ["zenodo-7313581", "zenodo-7631438", "zenodo-10605186", "zenodo-5001776"]
    assert len(preview["rows"]) == 4
    assert any("no real trial rows" in issue for issue in preview["issues"])


def test_v10_bench_preview_is_deterministic_and_ordered():
    root = Path(__file__).resolve().parents[2]
    preview_first = build_v10_bench_preview(root)
    preview_second = build_v10_bench_preview(root)

    assert preview_first["materials"] == preview_second["materials"]
    assert preview_first["rows"] == preview_second["rows"]
    assert preview_first["materials"] == [row["source_id"] for row in preview_first["rows"]]
    assert preview_first["materials"] == [
        "zenodo-7313581",
        "zenodo-7631438",
        "zenodo-10605186",
        "zenodo-5001776",
    ]
