from __future__ import annotations

import argparse
import json

from v43predictions_core import evaluate_v43_astro, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V43 astrophysics predictions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v43_astro()
    payload = finalize_check(
        args.output_dir,
        "v43astro_check",
        "V43 astrophysics check",
        evaluation,
        [
            ("external_references", "external_references"),
            ("astro_predictions", "astro_predictions"),
            ("DM_signature", "DM_signature"),
            ("lensing_signature", "lensing_signature"),
            ("astro_summary", "astro_summary"),
            ("astro_verdict", "astro_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
