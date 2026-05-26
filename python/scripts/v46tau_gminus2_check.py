from __future__ import annotations

import argparse
import json

from v46tau_core import evaluate_v46_tau_gminus2, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V46 tau g-2 check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v46_tau_gminus2()
    payload = finalize_check(
        args.output_dir,
        "v46tau_gminus2_check",
        "V46 tau g-2 check",
        evaluation,
        [
            ("m_tau", "m_tau"),
            ("delta_a_tau_model", "delta_a_tau_model"),
            ("delta_a_tau_bound_ok", "delta_a_tau_bound_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()