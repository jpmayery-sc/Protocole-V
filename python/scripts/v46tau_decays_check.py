from __future__ import annotations

import argparse
import json

from v46tau_core import evaluate_v46_tau_decays, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V46 tau decays check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v46_tau_decays()
    payload = finalize_check(
        args.output_dir,
        "v46tau_decays_check",
        "V46 tau decays check",
        evaluation,
        [
            ("tau_decay_shifts", "tau_decay_shifts"),
            ("tau_decay_ok", "tau_decay_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()