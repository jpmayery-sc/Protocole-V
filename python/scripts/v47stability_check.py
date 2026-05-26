from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_stability, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 stability check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_stability()
    payload = finalize_check(
        args.output_dir,
        "v47stability_check",
        "V47 stability check",
        evaluation,
        [
            ("baryon_number_ok", "baryon_number_ok"),
            ("no_exotic_channels", "no_exotic_channels"),
            ("RG_consistency", "RG_consistency"),
            ("geometry_consistency", "geometry_consistency"),
            ("stability_ok", "stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()