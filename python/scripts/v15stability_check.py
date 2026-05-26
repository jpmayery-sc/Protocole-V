"""Measure the stability of the V15 locked model under small perturbations."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, PERTURBATION_LEVELS, evaluate_stability_case, final_locked_theta, workspace_root


def evaluate_stability() -> dict:
    theta = final_locked_theta()
    rows = []
    all_supported = True
    for name in FINAL_LOCKED_NAMES:
        for level in PERTURBATION_LEVELS:
            row = evaluate_stability_case(theta, name, level)
            rows.append(row)
            all_supported = all_supported and bool(row["plus_supported"]) and bool(row["minus_supported"])

    verdict = "supported" if all_supported else "falsified"
    return {
        "reduced_theta": theta,
        "rows": rows,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_stability()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le modele reduit reste stable sous de petites perturbations des 5 parametres verrouilles",
        "case_control": "perturbations relatives 1%, 5% et 10% autour du vecteur reduit",
        "observable": "z_geo, z_int, z_canal, z_mod, alpha_residual, fine_delta",
        "expected": "toutes les perturbations restent supportees et la calibration ne casse pas",
        "measured": {
            "locked_names": FINAL_LOCKED_NAMES,
            "frozen_names": FINAL_FROZEN_NAMES,
            "perturbation_levels": PERTURBATION_LEVELS,
            "supported_cases": sum(1 for row in result["rows"] if row["plus_supported"] and row["minus_supported"]),
            "total_cases": len(result["rows"]),
        },
        "rows": result["rows"],
        "reduced_theta": result["reduced_theta"],
        "verdict": result["verdict"],
        "reference": "V15 stability consolidation",
    }

    json_path = outdir / f"v15stability_check_{timestamp}.json"
    txt_path = outdir / f"v15stability_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V15 stability check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"locked_names: {', '.join(FINAL_LOCKED_NAMES)}",
        f"frozen_names: {', '.join(FINAL_FROZEN_NAMES)}",
        f"supported_cases: {payload['measured']['supported_cases']}/{payload['measured']['total_cases']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the stability of the V15 locked model.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()