from __future__ import annotations

import argparse
import json

from v41symmetries_core import evaluate_v41_continuous, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V41 continuous symmetry check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v41_continuous()
    payload = finalize_check(
        args.output_dir,
        "v41continuous_check",
        "V41 continuous symmetry check",
        evaluation,
        [
            ("diff_invariance_ok", "diff_invariance_ok"),
            ("KT_rotation_symmetry", "KT_rotation_symmetry"),
            ("internal_U1_Y", "internal_U1_Y"),
            ("continuous_symmetry_summary", "continuous_symmetry_summary"),
            ("v41_continuous_verdict", "v41_continuous_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
