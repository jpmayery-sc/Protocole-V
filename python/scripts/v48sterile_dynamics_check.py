from __future__ import annotations

import argparse
import json

from v48neutrinos_core import evaluate_v48_sterile_dynamics, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V48 sterile dynamics check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v48_sterile_dynamics()
    payload = finalize_check(
        args.output_dir,
        "v48sterile_dynamics_check",
        "V48 sterile dynamics check",
        evaluation,
        [
            ("geometric_mass_shift", "geometric_mass_shift"),
            ("rg_stability_ok", "rg_stability_ok"),
            ("no_tachyon_ok", "no_tachyon_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()