from __future__ import annotations

import json
from pathlib import Path

import pytest

from v10_sources import summarize_v10_sources


pytestmark = pytest.mark.flow


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_path() -> Path:
    return repo_root() / "python" / "data" / "v10_sources_manifest.json"


def test_v10_manifest_lists_prepared_sources():
    manifest = load_json(manifest_path())
    sources = {entry["id"]: entry for entry in manifest["external_sources"]}

    assert manifest["schema_version"] == 1
    assert manifest["status"] == "partial"
    assert {"zenodo-7313581", "zenodo-7631438", "zenodo-10605186", "zenodo-5001776"} <= set(sources)

    for source_id in ("zenodo-7313581", "zenodo-7631438", "zenodo-10605186", "zenodo-5001776"):
        entry = sources[source_id]
        assert entry["record_url"].startswith("https://zenodo.org/records/")
        assert entry["local_ingest_path"].endswith("ingest_index.json")
        assert entry["local_readme_path"].endswith("README.md")
        assert (repo_root() / entry["local_ingest_path"]).exists()
        assert (repo_root() / entry["local_readme_path"]).exists()


@pytest.mark.parametrize(
    ("source_id", "expected_status", "check_fn"),
    [
        ("zenodo-7313581", "partial", lambda obj: obj["derived_summary"]["conversion_rows"] == 34 and obj["derived_summary"]["noise_rows"] == 10),
        ("zenodo-7631438", "partial", lambda obj: obj["extracted_tables"]["figure2_population_output"][1][1] > 0.5 and obj["derived_summary"]["figure5_fidelity_trend"] == "increasing with time for n=47 and n=55"),
        ("zenodo-10605186", "metadata_only", lambda obj: obj["schema_coverage"]["target_fidelity"] and not obj["schema_coverage"]["direct_material"] and obj["archive_size_bytes"] > 2_000_000_000),
        ("zenodo-5001776", "metadata_only", lambda obj: obj["extracted_points"]["alpha_fidelity_sample"][0] == [1.24, 0.7972329534498205] and "Mathematica" in obj["derived_summary"]["required_tools"]),
    ],
)
def test_v10_source_indexes_are_structurally_sound(source_id: str, expected_status: str, check_fn):
    manifest = load_json(manifest_path())
    source_entry = next(entry for entry in manifest["external_sources"] if entry["id"] == source_id)
    index_path = repo_root() / source_entry["local_ingest_path"]
    index = load_json(index_path)

    assert source_entry["fit_for_v10"] in {"ingested_partial", "metadata_only"}
    assert index["status"] == expected_status
    assert check_fn(index)


def test_v10_bridge_summary_aggregates_all_prepared_sources():
    summary = summarize_v10_sources(repo_root())

    assert summary["manifest_status"] == "partial"
    assert summary["schema_version"] == 1
    assert summary["source_count"] == 4
    assert summary["bridge_ready_count"] == 4
    assert summary["status_counts"]["partial"] == 2
    assert summary["status_counts"]["metadata_only"] == 2
    assert summary["has_direct_material_count"] == 0

    sources = {entry["id"]: entry for entry in summary["sources"]}
    assert sources["zenodo-7313581"]["raw_file_count"] == 2
    assert sources["zenodo-7631438"]["raw_file_count"] == 4
    assert sources["zenodo-10605186"]["source_type"] == "simulation"
    assert sources["zenodo-5001776"]["bridge_value"] == "loss resilience and measurement imperfection modeling"
