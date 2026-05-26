from __future__ import annotations

import argparse
import json

from v43predictions_core import evaluate_v43_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V43 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v43_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v43synthesis_check",
        "V43 synthesis check",
        evaluation,
        [
            ("external_references", "external_references"),
            ("predictions_table", "predictions_table"),
            ("falsifiability_ok", "falsifiability_ok"),
            ("v43_global_verdict", "v43_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
