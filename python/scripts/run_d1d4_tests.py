"""Run the D1 / D4 series and report the final suite verdict."""
from __future__ import annotations

import argparse
import json

from run_d1d4_suite import run_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the D1 / D4 series and report the final verdict.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime and suite outputs")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    summary = result.get("summary", {})
    verdict = summary.get("overall_verdict", "unknown")
    print(f"D1/D4 final verdict: {verdict}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()