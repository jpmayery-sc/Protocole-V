from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v41synthesis_check",
        "V41 synthesis check",
        evaluation,
        [
            ("continuous_symmetry_summary", "continuous_symmetry_summary"),
            ("discrete_symmetry_summary", "discrete_symmetry_summary"),
            ("geometric_symmetry_summary", "geometric_symmetry_summary"),
            ("conserved_quantities_summary", "conserved_quantities_summary"),
            ("symmetry_structure_ok", "symmetry_structure_ok"),
            ("v41_global_verdict", "v41_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
