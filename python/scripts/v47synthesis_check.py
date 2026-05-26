from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v47synthesis_check",
        "V47 synthesis check",
        evaluation,
        [
            ("baryon_mass_summary", "baryon_mass_summary"),
            ("splitting_summary", "splitting_summary"),
            ("beta_decay_summary", "beta_decay_summary"),
            ("nuclear_summary", "nuclear_summary"),
            ("stability_summary", "stability_summary"),
            ("v47_global_verdict", "v47_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()