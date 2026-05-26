from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_renormality, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 renormality check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_renormality()
    payload = finalize_check(
        args.output_dir,
        "v42renormality_check",
        "V42 renormality check",
        evaluation,
        [
            ("EFT_validity_ok", "EFT_validity_ok"),
            ("RG_flow_stable", "RG_flow_stable"),
            ("renormality_summary", "renormality_summary"),
            ("v42_renormality_verdict", "v42_renormality_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
