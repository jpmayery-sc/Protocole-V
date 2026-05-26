from __future__ import annotations

import argparse
import json

from v44potential_core import evaluate_v44_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v44_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v44synthesis_check",
        "V44 synthesis check",
        evaluation,
        [
            ("decomposition_summary", "decomposition_summary"),
            ("kt_potential_summary", "kt_potential_summary"),
            ("y_potential_summary", "y_potential_summary"),
            ("coupling_summary", "coupling_summary"),
            ("stability_summary", "stability_summary"),
            ("v44_global_verdict", "v44_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()