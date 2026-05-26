from __future__ import annotations

import argparse
import json

from v48neutrinos_core import evaluate_v48_mass_model, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V48 mass model check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v48_mass_model()
    payload = finalize_check(
        args.output_dir,
        "v48mass_model_check",
        "V48 mass model check",
        evaluation,
        [
            ("heavy_neutrino_masses", "heavy_neutrino_masses"),
            ("mass_model_ok", "mass_model_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()