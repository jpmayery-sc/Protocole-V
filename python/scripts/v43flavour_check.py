from __future__ import annotations

import argparse
import json

from v43predictions_core import evaluate_v43_flavour, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V43 flavour predictions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v43_flavour()
    payload = finalize_check(
        args.output_dir,
        "v43flavour_check",
        "V43 flavour check",
        evaluation,
        [
            ("external_references", "external_references"),
            ("flavour_predictions", "flavour_predictions"),
            ("RK_prediction", "RK_prediction"),
            ("LFU_prediction", "LFU_prediction"),
            ("flavour_summary", "flavour_summary"),
            ("flavour_verdict", "flavour_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
