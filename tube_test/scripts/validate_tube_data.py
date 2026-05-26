"""Validate that the tube-test data files exist and are readable."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tube_test.scripts.run_tube_suite import workspace_root, load_manifest


def validate_json(path: Path) -> None:
    json.loads(path.read_text(encoding="utf-8"))


def validate_csv(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if not header:
            raise ValueError(f"CSV file has no header: {path}")
        next(reader, None)


def validate_dataset_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        validate_json(path)
    elif path.suffix.lower() == ".csv":
        validate_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate tube-test data files.")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to the manifest JSON file",
    )
    args = parser.parse_args()

    root = workspace_root()
    tube_root = root / "tube_test"
    manifest_path = Path(args.manifest) if args.manifest else tube_root / "data" / "manifest.json"
    manifest = load_manifest(manifest_path)

    checked: list[str] = []
    for dataset in manifest.get("datasets", []):
        dataset_path = tube_root / dataset["path"]
        validate_dataset_file(dataset_path)
        checked.append(dataset["name"])

        companion_path = dataset.get("companion_path")
        if companion_path:
            validate_dataset_file(tube_root / companion_path)

    print(json.dumps({"status": "ok", "checked": checked}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()