from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_geometric, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 geometric symmetry check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_geometric()
    payload = finalize_check(
        args.output_dir,
        "v41geometric_check",
        "V41 geometric symmetry check",
        evaluation,
        [
            ("D1D2_symmetry_ok", "D1D2_symmetry_ok"),
            ("rescaling_symmetry_ok", "rescaling_symmetry_ok"),
            ("geometric_symmetry_summary", "geometric_symmetry_summary"),
            ("v41_geometric_verdict", "v41_geometric_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
