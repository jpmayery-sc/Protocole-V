from __future__ import annotations

import argparse
import json

from v45rgflow_core import evaluate_v45_fixed_points, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V45 fixed points check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v45_fixed_points()
    payload = finalize_check(
        args.output_dir,
        "v45fixed_points_check",
        "V45 fixed points check",
        evaluation,
        [
            ("fixed_points", "fixed_points"),
            ("IR_fixed_point_ok", "IR_fixed_point_ok"),
            ("UV_fixed_point_ok", "UV_fixed_point_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()