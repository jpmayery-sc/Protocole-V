from __future__ import annotations

import argparse
import json

from v47baryons_core import evaluate_v47_qcd_masses, finalize_check


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V47 QCD masses check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    evaluation = evaluate_v47_qcd_masses()
    payload = finalize_check(
        args.output_dir,
        "v47qcd_masses_check",
        "V47 QCD masses check",
        evaluation,
        [
            ("mass_shifts", "mass_shifts"),
            ("baryon_mass_ok", "baryon_mass_ok"),
        ],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()