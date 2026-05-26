"""Run the Electron-5 extended series and print the final suite verdict."""
from __future__ import annotations

import argparse
import json

from run_electron5_extended_suite import run_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Electron-5 extended series and print the final verdict.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    verdict = result.get("overall_verdict", "unknown")
    print(f"Electron-5 extended final verdict: {verdict}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()