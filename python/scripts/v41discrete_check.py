from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_discrete, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 discrete symmetry check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_discrete()
    payload = finalize_check(
        args.output_dir,
        "v41discrete_check",
        "V41 discrete symmetry check",
        evaluation,
        [
            ("Z2_Y_ok", "Z2_Y_ok"),
            ("Z2_KT_ok", "Z2_KT_ok"),
            ("discrete_symmetry_summary", "discrete_symmetry_summary"),
            ("v41_discrete_verdict", "v41_discrete_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
