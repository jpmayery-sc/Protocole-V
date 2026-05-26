"""Helpers for loading and summarizing the local V10 source base."""
from __future__ import annotations

import json
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_path(root: Path | None = None) -> Path:
    resolved_root = root or workspace_root()
    return resolved_root / "python" / "data" / "v10_sources_manifest.json"


def load_manifest(root: Path | None = None) -> dict:
    return load_json(manifest_path(root))


def resolve_path(root: Path, relative_path: str) -> Path:
    return root / relative_path.replace("/", "\\")


def load_source_index(root: Path, source_entry: dict) -> dict:
    ingest_path = resolve_path(root, source_entry["local_ingest_path"])
    return load_json(ingest_path)


def summarize_v10_sources(root: Path | None = None) -> dict:
    resolved_root = root or workspace_root()
    manifest = load_manifest(resolved_root)
    sources = []
    status_counts: dict[str, int] = {}

    for entry in manifest.get("external_sources", []):
        local_ingest_path = entry.get("local_ingest_path")
        local_readme_path = entry.get("local_readme_path")
        source = {
            "id": entry["id"],
            "title": entry["title"],
            "fit_for_v10": entry.get("fit_for_v10", "unknown"),
            "local_ingest_path": local_ingest_path,
            "local_readme_path": local_readme_path,
            "ingest_exists": bool(local_ingest_path and resolve_path(resolved_root, local_ingest_path).exists()),
            "readme_exists": bool(local_readme_path and resolve_path(resolved_root, local_readme_path).exists()),
        }

        if source["ingest_exists"]:
            index = load_source_index(resolved_root, entry)
            source["index_status"] = index.get("status", "unknown")
            source["index_fit_for_v10"] = index.get("fit_for_v10", "unknown")
            source["raw_file_count"] = len(index.get("raw_files", []))
            source["source_type"] = index.get("derived_summary", {}).get("source_type")
            source["bridge_value"] = index.get("derived_summary", {}).get("bridge_value")
            source["direct_material"] = bool(index.get("schema_coverage", {}).get("direct_material", False))
            status = source["index_status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        else:
            source["index_status"] = "missing"
            source["raw_file_count"] = 0
            source["source_type"] = None
            source["bridge_value"] = None
            source["direct_material"] = False
            status_counts["missing"] = status_counts.get("missing", 0) + 1

        sources.append(source)

    return {
        "manifest_status": manifest.get("status", "unknown"),
        "schema_version": manifest.get("schema_version"),
        "source_count": len(sources),
        "status_counts": status_counts,
        "sources": sources,
        "bridge_ready_count": sum(1 for source in sources if source["index_status"] in {"partial", "metadata_only"}),
        "has_direct_material_count": sum(1 for source in sources if source.get("direct_material")),
    }
