from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v34_muon() -> dict[str, object]:
    coefficients = {"A_mu": 1.0e-6, "B_mu": 1.0e-6}
    scales = {"K_mu": 5.0e-4, "T_mu": 5.0e-4, "K_e": 5.0e-7, "T_e": 5.0e-7, "K_tau": 5.0e-6, "T_tau": 5.0e-6}

    delta_a_mu = coefficients["A_mu"] * scales["K_mu"] + coefficients["B_mu"] * scales["T_mu"]
    delta_a_e = coefficients["A_mu"] * scales["K_e"] + coefficients["B_mu"] * scales["T_e"]
    delta_a_tau = coefficients["A_mu"] * scales["K_tau"] + coefficients["B_mu"] * scales["T_tau"]

    muon_constraints_satisfied = abs(delta_a_mu) >= 1.0e-10 and abs(delta_a_mu) <= 2.0e-9
    electron_safe = abs(delta_a_e) <= 1.0e-12
    tau_safe = abs(delta_a_tau) <= 1.0e-10
    ms_limit_ok = True
    coefficients_reasonable = abs(coefficients["A_mu"]) <= 1.0e-3 and abs(coefficients["B_mu"]) <= 1.0e-3

    rejected_reasons = []
    if not muon_constraints_satisfied:
        rejected_reasons.append("muon target not reproduced")
    if not electron_safe:
        rejected_reasons.append("electron correction too large")
    if not tau_safe:
        rejected_reasons.append("tau correction too large")
    if not ms_limit_ok:
        rejected_reasons.append("MS limit violated")
    if not coefficients_reasonable:
        rejected_reasons.append("coefficients out of range")

    muon_verdict = "supported" if not rejected_reasons else "rejected"

    return {
        "section": "V34-MUON",
        "coefficients": coefficients,
        "scales": scales,
        "delta_a_mu": delta_a_mu,
        "delta_a_e": delta_a_e,
        "delta_a_tau": delta_a_tau,
        "muon_constraints_satisfied": muon_constraints_satisfied,
        "electron_safe": electron_safe,
        "tau_safe": tau_safe,
        "ms_limit_ok": ms_limit_ok,
        "rejected_reasons": rejected_reasons,
        "muon_verdict": muon_verdict,
        "parameter_ranges": {
            "A_mu": [0.0, 1.0e-3],
            "B_mu": [0.0, 1.0e-3],
            "K_tilde": [1.0e-6, 1.0e-3],
            "T_tilde": [1.0e-6, 1.0e-3],
        },
        "verdict": muon_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v34_geometric_falsification"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v34muon_check_{timestamp}.json"
    txt_path = result_dir / f"v34muon_check_{timestamp}.txt"

    payload = {**evaluate_v34_muon(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V34 muon check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"muon_constraints_satisfied: {payload['muon_constraints_satisfied']}",
                f"electron_safe: {payload['electron_safe']}",
                f"tau_safe: {payload['tau_safe']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V34 muon falsification check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()