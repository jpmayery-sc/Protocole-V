from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_loops, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 loops check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_loops()
    payload = finalize_check(
        args.output_dir,
        "v42loops_check",
        "V42 loops check",
        evaluation,
        [
            ("loop_corrections", "loop_corrections"),
            ("naturality_ok", "naturality_ok"),
            ("divergence_control_ok", "divergence_control_ok"),
            ("v42_loops_verdict", "v42_loops_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
