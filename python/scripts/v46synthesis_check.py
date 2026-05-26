from __future__ import annotations

import argparse
import json

from v46tau_core import evaluate_v46_synthesis, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V46 synthesis check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v46_synthesis()
    payload = finalize_check(
        args.output_dir,
        "v46synthesis_check",
        "V46 synthesis check",
        evaluation,
        [
            ("tau_gminus2_summary", "tau_gminus2_summary"),
            ("tau_decay_summary", "tau_decay_summary"),
            ("tau_LFU_summary", "tau_LFU_summary"),
            ("multisector_summary", "multisector_summary"),
            ("v46_global_verdict", "v46_global_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()