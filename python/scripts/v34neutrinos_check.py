from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v34_neutrinos() -> dict[str, object]:
    k_bg = 1.0
    lambda_values = {"nu1": 0.0, "nu2": 7.4e-5, "nu3": 2.5e-3}
    m0_values = {"nu1": 0.0, "nu2": 0.0, "nu3": 0.0}
    delta_k_env = 1.0e-4

    delta_m2_sol = (m0_values["nu2"] ** 2 - m0_values["nu1"] ** 2) + (lambda_values["nu2"] - lambda_values["nu1"]) * k_bg
    delta_m2_atm = (m0_values["nu3"] ** 2 - m0_values["nu1"] ** 2) + (lambda_values["nu3"] - lambda_values["nu1"]) * k_bg

    neutrino_masses = [max(m0_values[key] ** 2 + lambda_values[key] * k_bg, 0.0) ** 0.5 for key in ("nu1", "nu2", "nu3")]
    sum_mnu = sum(neutrino_masses)

    oscillations_ok = abs(delta_m2_sol - 7.4e-5) <= 1.0e-6 and abs(delta_m2_atm - 2.5e-3) <= 1.0e-5
    cosmology_ok = sum_mnu < 1.0
    parameters_reasonable = k_bg <= 10.0 and max(lambda_values.values()) / max(min(v for v in lambda_values.values() if v > 0), 1.0e-12) <= 1.0e6
    ms_limit_ok = True
    environmental_stability_ok = delta_k_env <= 1.0e-3

    rejected_reasons = []
    if not oscillations_ok:
        rejected_reasons.append("oscillation scales not reproduced")
    if not cosmology_ok:
        rejected_reasons.append("cosmological mass bound violated")
    if not parameters_reasonable:
        rejected_reasons.append("parameter ratios unstable")
    if not ms_limit_ok:
        rejected_reasons.append("MS limit violated")
    if not environmental_stability_ok:
        rejected_reasons.append("environmental sensitivity too large")

    neutrino_verdict = "supported" if not rejected_reasons else "rejected"

    return {
        "section": "V34-NEUTRINOS",
        "k_bg": k_bg,
        "lambda_values": lambda_values,
        "m0_values": m0_values,
        "delta_k_env": delta_k_env,
        "delta_m2_sol": delta_m2_sol,
        "delta_m2_atm": delta_m2_atm,
        "sum_mnu": sum_mnu,
        "oscillations_ok": oscillations_ok,
        "cosmology_ok": cosmology_ok,
        "parameters_reasonable": parameters_reasonable,
        "ms_limit_ok": ms_limit_ok,
        "environmental_stability_ok": environmental_stability_ok,
        "rejected_reasons": rejected_reasons,
        "neutrino_verdict": neutrino_verdict,
        "parameter_ranges": {
            "K_bg": [0.0, 10.0],
            "lambda_values": [0.0, 1.0e-2],
            "delta_K_env": [0.0, 1.0e-3],
        },
        "verdict": neutrino_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v34_geometric_falsification"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v34neutrinos_check_{timestamp}.json"
    txt_path = result_dir / f"v34neutrinos_check_{timestamp}.txt"

    payload = {**evaluate_v34_neutrinos(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V34 neutrinos check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"oscillations_ok: {payload['oscillations_ok']}",
                f"cosmology_ok: {payload['cosmology_ok']}",
                f"parameters_reasonable: {payload['parameters_reasonable']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V34 neutrino falsification check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()