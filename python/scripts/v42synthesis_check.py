from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v42synthesis_check",
        "V42 synthesis check",
        evaluation,
        [
            ("propagator_summary", "propagator_summary"),
            ("vertex_summary", "vertex_summary"),
            ("loop_summary", "loop_summary"),
            ("renormality_summary", "renormality_summary"),
            ("quantum_structure_ok", "quantum_structure_ok"),
            ("v42_global_verdict", "v42_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
