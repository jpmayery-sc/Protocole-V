from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_nuclear_binding, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 nuclear binding check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_nuclear_binding()
    payload = finalize_check(
        args.output_dir,
        "v47nuclear_binding_check",
        "V47 nuclear binding check",
        evaluation,
        [
            ("binding_shifts", "binding_shifts"),
            ("BBN_ok", "BBN_ok"),
            ("nuclear_ok", "nuclear_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()