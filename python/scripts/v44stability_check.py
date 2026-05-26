from __future__ import annotations

import argparse
import json

from v44potential_core import evaluate_v44_stability, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 stability check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v44_stability()
    payload = finalize_check(
        args.output_dir,
        "v44stability_check",
        "V44 stability check",
        evaluation,
        [
            ("hessian_matrix", "hessian_matrix"),
            ("eigenvalues", "eigenvalues"),
            ("global_minimum", "global_minimum"),
            ("no_secondary_minima", "no_secondary_minima"),
            ("stability_ok", "stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()