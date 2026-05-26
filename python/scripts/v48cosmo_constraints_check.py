from __future__ import annotations

import argparse
import json

from v48neutrinos_core import evaluate_v48_cosmo_constraints, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V48 cosmology constraints check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v48_cosmo_constraints()
    payload = finalize_check(
        args.output_dir,
        "v48cosmo_constraints_check",
        "V48 cosmology constraints check",
        evaluation,
        [
            ("delta_neff", "delta_neff"),
            ("sum_mnu", "sum_mnu"),
            ("cosmology_ok", "cosmology_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()