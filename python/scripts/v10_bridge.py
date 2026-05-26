"""Build a provenance-safe bridge summary from the V10 source base."""
from __future__ import annotations

from pathlib import Path

from v10_sources import summarize_v10_sources, workspace_root


def build_v10_bridge(root: Path | None = None) -> dict:
    resolved_root = root or workspace_root()
    source_summary = summarize_v10_sources(resolved_root)

    rows = []
    for source in source_summary["sources"]:
        rows.append(
            {
                "source_id": source["id"],
                "title": source["title"],
                "index_status": source["index_status"],
                "source_type": source["source_type"],
                "bridge_value": source["bridge_value"],
                "direct_material": source["direct_material"],
                "bridge_ready": source["index_status"] in {"partial", "metadata_only"},
                "local_ingest_path": source["local_ingest_path"],
                "local_readme_path": source["local_readme_path"],
            }
        )

    return {
        "suite": "v10_bridge",
        "manifest_status": source_summary["manifest_status"],
        "source_count": source_summary["source_count"],
        "bridge_ready_count": source_summary["bridge_ready_count"],
        "rows": rows,
    }


def build_v10_bench_preview(root: Path | None = None) -> dict:
    bridge = build_v10_bridge(root)
    materials = [row["source_id"] for row in bridge["rows"]]

    return {
        "suite": "v10_bench_preview",
        "overall_verdict": "blocked",
        "input_status": "metadata_only",
        "source_count": bridge["source_count"],
        "bridge_ready_count": bridge["bridge_ready_count"],
        "materials": materials,
        "issues": [
            "no real trial rows were generated from the V10 bridge",
            "the ECGP bench remains trial-only until a real measurement table exists",
        ],
        "rows": bridge["rows"],
    }
