"""Validate the nuclear-stability protocol used in the V4 dossier."""
from __future__ import annotations

import argparse
import json

from h_fe_pb_check import run_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V4 nuclear stability check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir, stem="nzstability_check")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()