from __future__ import annotations

import argparse
import json

from v46tau_core import evaluate_v46_tau_stability, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V46 tau stability check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v46_tau_stability()
    payload = finalize_check(
        args.output_dir,
        "v46tau_stability_check",
        "V46 tau stability check",
        evaluation,
        [
            ("multisector_consistency", "multisector_consistency"),
            ("RG_consistency", "RG_consistency"),
            ("geometry_consistency", "geometry_consistency"),
            ("stability_ok", "stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()