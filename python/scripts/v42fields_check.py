from __future__ import annotations

import argparse
import json

from v42quantum_core import evaluate_v42_fields, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V42 fields check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v42_fields()
    payload = finalize_check(
        args.output_dir,
        "v42fields_check",
        "V42 fields check",
        evaluation,
        [
            ("field_list", "field_list"),
            ("mass_dimensions", "mass_dimensions"),
            ("canonical_normalization_ok", "canonical_normalization_ok"),
            ("v42_fields_verdict", "v42_fields_verdict"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
