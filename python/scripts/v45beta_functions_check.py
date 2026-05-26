from __future__ import annotations

import argparse
import json

from v45rgflow_core import evaluate_v45_beta_functions, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V45 beta functions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v45_beta_functions()
    payload = finalize_check(
        args.output_dir,
        "v45beta_functions_check",
        "V45 beta functions check",
        evaluation,
        [
            ("beta_functions", "beta_functions"),
            ("RG_equations", "RG_equations"),
            ("beta_ok", "beta_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()