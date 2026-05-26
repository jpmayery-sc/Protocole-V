from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_qcd_splittings, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 QCD splittings check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_qcd_splittings()
    payload = finalize_check(
        args.output_dir,
        "v47qcd_splittings_check",
        "V47 QCD splittings check",
        evaluation,
        [
            ("splitting_shifts", "splitting_shifts"),
            ("splitting_ok", "splitting_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()