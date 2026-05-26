from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v35_muon() -> dict[str, object]:
    target = 1.0e-9
    coefficient_grid = [5.0e-7, 1.0e-6, 2.0e-6]
    scale_grid = [2.0e-4, 5.0e-4, 8.0e-4]

    best_point: dict[str, float] | None = None
    best_score = math.inf
    scan_count = 0

    for a_mu in coefficient_grid:
        for b_mu in coefficient_grid:
            for k_tilde in scale_grid:
                for t_tilde in scale_grid:
                    scan_count += 1
                    delta_a_mu = a_mu * k_tilde + b_mu * t_tilde
                    delta_a_e = a_mu * 5.0e-7 + b_mu * 5.0e-7
                    delta_a_tau = a_mu * 5.0e-6 + b_mu * 5.0e-6
                    penalty = 0.0
                    if abs(delta_a_e) > 1.0e-12:
                        penalty += abs(delta_a_e) - 1.0e-12
                    if abs(delta_a_tau) > 1.0e-11:
                        penalty += abs(delta_a_tau) - 1.0e-11
                    score = abs(delta_a_mu - target) + penalty
                    if score < best_score:
                        best_score = score
                        best_point = {
                            "A_mu": a_mu,
                            "B_mu": b_mu,
                            "K_tilde": k_tilde,
                            "T_tilde": t_tilde,
                            "delta_a_mu": delta_a_mu,
                            "delta_a_e": delta_a_e,
                            "delta_a_tau": delta_a_tau,
                        }

    tolerance = 1.0e-18
    muon_target_hit = best_point is not None and abs(best_point["delta_a_mu"] - target) <= 5.0e-10
    electron_safe = best_point is not None and abs(best_point["delta_a_e"]) <= 1.0e-12 + tolerance
    tau_safe = best_point is not None and abs(best_point["delta_a_tau"]) <= 1.0e-11 + tolerance
    muon_verdict = "supported" if muon_target_hit and electron_safe and tau_safe else "rejected"

    rejected_reasons = []
    if not muon_target_hit:
        rejected_reasons.append("muon target not hit by scan")
    if not electron_safe:
        rejected_reasons.append("electron correction too large in scan")
    if not tau_safe:
        rejected_reasons.append("tau correction too large in scan")

    return {
        "section": "V35-MUON",
        "scan_count": scan_count,
        "best_muon_point": best_point,
        "best_muon_score": best_score,
        "muon_target_hit": muon_target_hit,
        "electron_safe": electron_safe,
        "tau_safe": tau_safe,
        "rejected_reasons": rejected_reasons,
        "muon_verdict": muon_verdict,
        "verdict": muon_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v35_numeric_calibration"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v35muon_scan_check_{timestamp}.json"
    txt_path = result_dir / f"v35muon_scan_check_{timestamp}.txt"

    payload = {**evaluate_v35_muon(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V35 muon scan check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"scan_count: {payload['scan_count']}",
                f"best_muon_score: {payload['best_muon_score']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V35 muon scan check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()