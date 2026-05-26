from __future__ import annotations

import argparse
import json

from v40effective_core import evaluate_v40_lagrangian, finalize_check


def run_check(output_dir=None):
    return finalize_check(
        output_dir,
        "v40lagrangian_check",
        "V40 lagrangian check",
        evaluate_v40_lagrangian(),
        [
            ("source_v39_supported", "source_v39_supported"),
            ("naturality_ok", "naturality_ok"),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V40 lagrangian check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()