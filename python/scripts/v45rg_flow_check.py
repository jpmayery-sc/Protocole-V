from __future__ import annotations

import argparse
import json

from v45rgflow_core import evaluate_v45_rg_flow, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V45 RG flow check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v45_rg_flow()
    payload = finalize_check(
        args.output_dir,
        "v45rg_flow_check",
        "V45 RG flow check",
        evaluation,
        [
            ("mu_grid", "mu_grid"),
            ("RG_trajectories", "RG_trajectories"),
            ("no_blowup_ok", "no_blowup_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()