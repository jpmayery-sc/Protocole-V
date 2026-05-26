from __future__ import annotations

import argparse
import json

from v44potential_core import evaluate_v44_couplings, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 couplings check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v44_couplings()
    payload = finalize_check(
        args.output_dir,
        "v44couplings_check",
        "V44 couplings check",
        evaluation,
        [
            ("xi", "xi"),
            ("eta", "eta"),
            ("coupling_naturality_ok", "coupling_naturality_ok"),
            ("coupling_stability_ok", "coupling_stability_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()