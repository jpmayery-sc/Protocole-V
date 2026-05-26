"""Validate the tube-test manifest structure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def validate_manifest(manifest_path: Path) -> dict:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    required_keys = ["suite", "omega", "fit_dataset", "datasets"]
    missing_keys = [key for key in required_keys if key not in payload]
    if missing_keys:
        raise ValueError(f"Missing keys: {', '.join(missing_keys)}")

    datasets = payload.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise ValueError("datasets must be a non-empty list")

    problems: list[str] = []
    for index, dataset in enumerate(datasets, start=1):
        if not isinstance(dataset, dict):
            problems.append(f"dataset #{index} is not an object")
            continue
        for key in ("name", "path", "observable", "source_url"):
            if key not in dataset or not dataset.get(key):
                problems.append(f"dataset #{index} is missing {key}")
        dataset_path = dataset.get("path", "")
        if isinstance(dataset_path, str) and Path(dataset_path).is_absolute():
            problems.append(f"dataset #{index} path must be relative: {dataset_path}")

    if problems:
        raise ValueError("; ".join(problems))

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the tube-test manifest.")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to the manifest JSON file",
    )
    args = parser.parse_args()

    root = workspace_root()
    default_manifest = root / "tube_test" / "data" / "manifest.json"
    manifest_path = Path(args.manifest) if args.manifest else default_manifest
    payload = validate_manifest(manifest_path)
    print(json.dumps({"status": "ok", "manifest": str(manifest_path), "datasets": len(payload["datasets"])}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()