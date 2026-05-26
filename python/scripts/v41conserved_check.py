from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_conserved, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 conserved quantities check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_conserved()
    payload = finalize_check(
        args.output_dir,
        "v41conserved_check",
        "V41 conserved quantities check",
        evaluation,
        [
            ("noether_currents", "noether_currents"),
            ("conserved_quantities", "conserved_quantities"),
            ("conserved_quantities_summary", "conserved_quantities_summary"),
            ("conservation_ok", "conservation_ok"),
            ("v41_conserved_verdict", "v41_conserved_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
