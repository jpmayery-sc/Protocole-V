from __future__ import annotations

import argparse
import json

from v44potential_core import evaluate_v44_y_potential, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 Y potential check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v44_y_potential()
    payload = finalize_check(
        args.output_dir,
        "v44y_potential_check",
        "V44 Y potential check",
        evaluation,
        [
            ("gamma", "gamma"),
            ("Y_inf", "Y_inf"),
            ("Y0", "Y0"),
            ("Y_mass", "Y_mass"),
            ("Y_stability_ok", "Y_stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()