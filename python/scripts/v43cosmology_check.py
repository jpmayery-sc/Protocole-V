from __future__ import annotations

import argparse
import json

from v43predictions_core import evaluate_v43_cosmology, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V43 cosmology predictions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v43_cosmology()
    payload = finalize_check(
        args.output_dir,
        "v43cosmology_check",
        "V43 cosmology check",
        evaluation,
        [
            ("external_references", "external_references"),
            ("cosmology_predictions", "cosmology_predictions"),
            ("fs8_prediction", "fs8_prediction"),
            ("H0_prediction", "H0_prediction"),
            ("Lambda_prediction", "Lambda_prediction"),
            ("cosmology_summary", "cosmology_summary"),
            ("cosmology_verdict", "cosmology_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
