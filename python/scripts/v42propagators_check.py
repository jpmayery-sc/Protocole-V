from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_propagators, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 propagators check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_propagators()
    payload = finalize_check(
        args.output_dir,
        "v42propagators_check",
        "V42 propagators check",
        evaluation,
        [
            ("propagator_K", "propagator_K"),
            ("propagator_T", "propagator_T"),
            ("propagator_Y", "propagator_Y"),
            ("positivity_ok", "positivity_ok"),
            ("v42_propagators_verdict", "v42_propagators_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
