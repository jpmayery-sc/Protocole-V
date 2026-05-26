from __future__ import annotations

import argparse
import json

from v45rgflow_core import evaluate_v45_stability, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V45 stability check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v45_stability()
    payload = finalize_check(
        args.output_dir,
        "v45stability_check",
        "V45 stability check",
        evaluation,
        [
            ("stability_matrix", "stability_matrix"),
            ("eigenvalues_RG", "eigenvalues_RG"),
            ("RG_stability_ok", "RG_stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()