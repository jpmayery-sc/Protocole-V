"""Run the regime flow check and print the final verdict."""
from __future__ import annotations

import argparse
import json

from regime_flow_check import run_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the regime flow check and print the final verdict.")
    parser.add_argument("--output-dir", default=None, help="Directory for the report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(f"Regime flow verdict: {result.get('verdict', 'unknown')}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()