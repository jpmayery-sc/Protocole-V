from __future__ import annotations

from pathlib import Path

import pytest

from v10_bridge import build_v10_bridge


pytestmark = pytest.mark.flow


def test_v10_bridge_stays_metadata_only():
    root = Path(__file__).resolve().parents[2]
    bridge = build_v10_bridge(root)

    assert bridge["manifest_status"] == "partial"
    assert bridge["source_count"] == 4
    assert bridge["bridge_ready_count"] == 4
    assert len(bridge["rows"]) == 4
    assert all(row["bridge_ready"] for row in bridge["rows"])
    assert not any(row["direct_material"] for row in bridge["rows"])

    ids = {row["source_id"] for row in bridge["rows"]}
    assert ids == {"zenodo-7313581", "zenodo-7631438", "zenodo-10605186", "zenodo-5001776"}


def test_v10_bridge_rows_exclude_trial_fields():
    root = Path(__file__).resolve().parents[2]
    bridge = build_v10_bridge(root)

    forbidden_keys = {
        "trial_id",
        "material",
        "frequency_hz",
        "measured_fidelity",
        "control_fidelity",
        "loss_db",
        "temperature_k",
        "geometry",
        "detector_counts",
    }
    allowed_keys = {
        "source_id",
        "title",
        "index_status",
        "source_type",
        "bridge_value",
        "direct_material",
        "bridge_ready",
        "local_ingest_path",
        "local_readme_path",
    }

    for row in bridge["rows"]:
        assert forbidden_keys.isdisjoint(row)
        assert set(row) == allowed_keys


def test_v10_bridge_aggregates_source_counts():
    root = Path(__file__).resolve().parents[2]
    bridge = build_v10_bridge(root)

    index_status_counts = {}
    source_types = set()
    bridge_values = set()

    for row in bridge["rows"]:
        index_status_counts[row["index_status"]] = index_status_counts.get(row["index_status"], 0) + 1
        if row["source_type"] is not None:
            source_types.add(row["source_type"])
        if row["bridge_value"] is not None:
            bridge_values.add(row["bridge_value"])

    assert bridge["source_count"] == 4
    assert bridge["bridge_ready_count"] == 4
    assert index_status_counts == {"partial": 2, "metadata_only": 2}
    assert source_types == {"simulation", "code_driven_dataset"}
    assert bridge_values == {
        "robustness and control-logic validation",
        "loss resilience and measurement imperfection modeling",
    }
