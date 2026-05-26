from __future__ import annotations

import argparse
import json

from v45rgflow_core import evaluate_v45_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V45 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v45_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v45synthesis_check",
        "V45 synthesis check",
        evaluation,
        [
            ("beta_summary", "beta_summary"),
            ("rg_flow_summary", "rg_flow_summary"),
            ("fixed_point_summary", "fixed_point_summary"),
            ("stability_summary", "stability_summary"),
            ("v45_global_verdict", "v45_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()