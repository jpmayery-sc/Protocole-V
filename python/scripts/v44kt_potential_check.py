from __future__ import annotations

import argparse
import json

from v44potential_core import evaluate_v44_kt_potential, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 KT potential check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v44_kt_potential()
    payload = finalize_check(
        args.output_dir,
        "v44kt_potential_check",
        "V44 KT potential check",
        evaluation,
        [
            ("lambda_K", "lambda_K"),
            ("lambda_T", "lambda_T"),
            ("lambda_KT", "lambda_KT"),
            ("KT_positive_definite", "KT_positive_definite"),
            ("KT_stability_ok", "KT_stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()