"""Validate the tube-test suite end to end."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tube_test.scripts.run_tube_suite import run_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the full tube-test suite.")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to the manifest JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for the validation summary",
    )
    args = parser.parse_args()

    result = run_suite(args.manifest, args.output_dir)
    if result.get("manifest_path", "").endswith("manifest.template.json"):
        raise RuntimeError("Suite validation must use the real manifest, not the template")
    if result.get("overall_verdict") != "supported":
        raise RuntimeError("Suite validation did not produce a supported verdict")
    if result.get("total", 0) < 3:
        raise RuntimeError("Suite validation expected at least 3 datasets")

    print(json.dumps({"status": "ok", "result": result}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()