"""Run the full D1 / D4 suite and then summarize the results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d1d4_suite_summary import run_summary as run_d1d4_summary


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "d1d4"
    return run_d1d4_summary(outdir, outdir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full D1 / D4 suite and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime and suite outputs")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()