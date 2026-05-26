from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v35_neutrinos() -> dict[str, object]:
    target_sol = 7.4e-5
    target_atm = 2.5e-3
    k_bg_grid = [0.5, 1.0, 2.0]
    lambda2_grid = [3.7e-5, 7.4e-5, 1.0e-4]
    lambda3_grid = [1.5e-3, 2.5e-3, 3.5e-3]

    best_point: dict[str, float] | None = None
    best_score = math.inf
    scan_count = 0

    for k_bg in k_bg_grid:
        for lambda2 in lambda2_grid:
            for lambda3 in lambda3_grid:
                scan_count += 1
                delta_m2_sol = lambda2 * k_bg
                delta_m2_atm = lambda3 * k_bg
                masses = [0.0, math.sqrt(max(lambda2 * k_bg, 0.0)), math.sqrt(max(lambda3 * k_bg, 0.0))]
                sum_mnu = sum(masses)
                penalty = 0.0
                if sum_mnu > 1.0:
                    penalty += sum_mnu - 1.0
                score = abs(delta_m2_sol - target_sol) + abs(delta_m2_atm - target_atm) + penalty
                if score < best_score:
                    best_score = score
                    best_point = {
                        "K_bg": k_bg,
                        "lambda_2": lambda2,
                        "lambda_3": lambda3,
                        "delta_m2_sol": delta_m2_sol,
                        "delta_m2_atm": delta_m2_atm,
                        "sum_mnu": sum_mnu,
                    }

    oscillations_hit = best_point is not None and abs(best_point["delta_m2_sol"] - target_sol) <= 1.0e-6 and abs(best_point["delta_m2_atm"] - target_atm) <= 1.0e-5
    cosmology_safe = best_point is not None and best_point["sum_mnu"] < 1.0
    parameters_reasonable = best_point is not None and best_point["K_bg"] <= 2.0 and best_point["lambda_3"] / max(best_point["lambda_2"], 1.0e-12) <= 1.0e6
    neutrino_verdict = "supported" if oscillations_hit and cosmology_safe and parameters_reasonable else "rejected"

    rejected_reasons = []
    if not oscillations_hit:
        rejected_reasons.append("oscillation targets not hit by scan")
    if not cosmology_safe:
        rejected_reasons.append("cosmological bound violated in scan")
    if not parameters_reasonable:
        rejected_reasons.append("parameter ratios unstable in scan")

    return {
        "section": "V35-NEUTRINOS",
        "scan_count": scan_count,
        "best_neutrino_point": best_point,
        "best_neutrino_score": best_score,
        "oscillations_hit": oscillations_hit,
        "cosmology_safe": cosmology_safe,
        "parameters_reasonable": parameters_reasonable,
        "rejected_reasons": rejected_reasons,
        "neutrino_verdict": neutrino_verdict,
        "verdict": neutrino_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v35_numeric_calibration"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v35neutrino_scan_check_{timestamp}.json"
    txt_path = result_dir / f"v35neutrino_scan_check_{timestamp}.txt"

    payload = {**evaluate_v35_neutrinos(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V35 neutrino scan check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"scan_count: {payload['scan_count']}",
                f"best_neutrino_score: {payload['best_neutrino_score']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V35 neutrino scan check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()