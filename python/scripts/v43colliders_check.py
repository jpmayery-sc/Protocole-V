from __future__ import annotations

import argparse
import json

from v43predictions_core import evaluate_v43_colliders, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V43 collider predictions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v43_colliders()
    payload = finalize_check(
        args.output_dir,
        "v43colliders_check",
        "V43 colliders check",
        evaluation,
        [
            ("external_references", "external_references"),
            ("collider_signatures", "collider_signatures"),
            ("predicted_deviations", "predicted_deviations"),
            ("collider_summary", "collider_summary"),
            ("collider_verdict", "collider_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
