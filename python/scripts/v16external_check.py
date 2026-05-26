"""Map internal V16 predictions to external observables."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v16prediction_core import evaluate_consistency, result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluation = evaluate_consistency()
    external = evaluation["external"]

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les sorties internes V16 se mappent vers des observables externes raisonnables",
        "case_control": "mapping interne vers externe",
        "observable": "z_obs, delta_nu_over_nu, delta_E, fine_correction_eff, grav_torsion_eff",
        "expected": "observables externes positives et compatibles avec z_mod",
        "measured": {
            "external_ok": evaluation["external_ok"],
            "consistency_ok": evaluation["consistency_ok"],
        },
        "internal": evaluation["internal"],
        "external": external,
        "verdict": "supported" if evaluation["external_ok"] else "falsified",
        "reference": "V16 external projection",
    }

    json_path = outdir / f"v16external_check_{timestamp}.json"
    txt_path = outdir / f"v16external_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V16 external check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"z_obs: {external['z_obs']}",
        f"delta_nu_over_nu: {external['delta_nu_over_nu']}",
        f"delta_E: {external['delta_E']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Map internal V16 predictions to external observables.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()