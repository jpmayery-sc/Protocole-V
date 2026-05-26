from __future__ import annotations

import argparse
import json

from v40effective_core import evaluate_v40_synthesis, finalize_check


def run_check(output_dir=None):
    return finalize_check(
        output_dir,
        "v40synthesis_check",
        "V40 synthesis check",
        evaluate_v40_synthesis(),
        [
            ("cosmology_consistency", "cosmology_consistency"),
            ("v40_global_verdict", "v40_global_verdict"),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V40 synthesis check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()