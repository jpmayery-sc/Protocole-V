from __future__ import annotations

import argparse
import json

from v46tau_core import evaluate_v46_tau_lfu, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V46 tau LFU check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v46_tau_lfu()
    payload = finalize_check(
        args.output_dir,
        "v46tau_lfu_check",
        "V46 tau LFU check",
        evaluation,
        [
            ("LFU_W_shift", "LFU_W_shift"),
            ("LFU_Z_shift", "LFU_Z_shift"),
            ("LFU_ok", "LFU_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()