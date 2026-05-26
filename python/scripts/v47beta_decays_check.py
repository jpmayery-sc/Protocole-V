from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_beta_decays, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 beta decays check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_beta_decays()
    payload = finalize_check(
        args.output_dir,
        "v47beta_decays_check",
        "V47 beta decays check",
        evaluation,
        [
            ("beta_decay_shift", "beta_decay_shift"),
            ("beta_decay_ok", "beta_decay_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()