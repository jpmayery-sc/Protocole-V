from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_interactions, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 interactions check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_interactions()
    payload = finalize_check(
        args.output_dir,
        "v42interactions_check",
        "V42 interactions check",
        evaluation,
        [
            ("vertex_table", "vertex_table"),
            ("coupling_strengths", "coupling_strengths"),
            ("interaction_ok", "interaction_ok"),
            ("v42_interactions_verdict", "v42_interactions_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
