from __future__ import annotations

import argparse
import json

from v48neutrinos_core import evaluate_v48_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V48 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v48_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v48synthesis_check",
        "V48 synthesis check",
        evaluation,
        [
            ("mass_model_summary", "mass_model_summary"),
            ("mixing_summary", "mixing_summary"),
            ("sterile_dynamics_summary", "sterile_dynamics_summary"),
            ("cosmology_summary", "cosmology_summary"),
            ("decay_summary", "decay_summary"),
            ("v48_global_verdict", "v48_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()