from __future__ import annotations

import argparse
import json

from v48neutrinos_core import evaluate_v48_decays, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V48 decays check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v48_decays()
    payload = finalize_check(
        args.output_dir,
        "v48decays_check",
        "V48 decays check",
        evaluation,
        [
            ("decay_widths", "decay_widths"),
            ("lifetime_years", "lifetime_years"),
            ("no_xray_violation", "no_xray_violation"),
            ("no_nuclear_violation", "no_nuclear_violation"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()