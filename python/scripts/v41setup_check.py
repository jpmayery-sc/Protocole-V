from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_setup, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 setup symmetry check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_setup()
    payload = finalize_check(
        args.output_dir,
        "v41setup_check",
        "V41 setup symmetry check",
        evaluation,
        [
            ("effective_lagrangian", "effective_lagrangian"),
            ("setup_ok", "setup_ok"),
            ("v41_setup_verdict", "v41_setup_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
