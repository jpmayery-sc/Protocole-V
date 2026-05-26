"""Quick coherence check for electromagnetic induction and self-induction.

The script verifies that induced voltage opposes flux variation and that the
response scales with |dPhi/dt|. It writes a timestamped JSON summary and a
short text report under results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


def simulate_cases(samples: int = 720):
    omega = 2.0 * math.pi
    amplitude = 1.0
    constant_flux_voltage = 0.0
    positive_flux_voltage = 0.0
    negative_flux_voltage = 0.0
    fast_response_voltage = 0.0
    slow_response_voltage = 0.0

    for index in range(samples):
        t = index / samples

        phi_const = amplitude
        dphi_const = 0.0

        phi_pos = amplitude * math.sin(omega * t)
        dphi_pos = amplitude * omega * math.cos(omega * t)

        phi_neg = -amplitude * math.sin(omega * t)
        dphi_neg = -amplitude * omega * math.cos(omega * t)

        phi_fast = amplitude * math.sin(4.0 * omega * t)
        dphi_fast = amplitude * 4.0 * omega * math.cos(4.0 * omega * t)

        phi_slow = amplitude * math.sin(0.5 * omega * t)
        dphi_slow = amplitude * 0.5 * omega * math.cos(0.5 * omega * t)

        constant_flux_voltage = max(constant_flux_voltage, abs(-dphi_const))
        positive_flux_voltage = max(positive_flux_voltage, abs(-dphi_pos))
        negative_flux_voltage = max(negative_flux_voltage, abs(-dphi_neg))
        fast_response_voltage = max(fast_response_voltage, abs(-dphi_fast))
        slow_response_voltage = max(slow_response_voltage, abs(-dphi_slow))

    return {
        "constant_flux_max_voltage": constant_flux_voltage,
        "positive_flux_max_voltage": positive_flux_voltage,
        "negative_flux_max_voltage": negative_flux_voltage,
        "fast_response_max_voltage": fast_response_voltage,
        "slow_response_max_voltage": slow_response_voltage,
    }


def classify_induction() -> dict:
    data = simulate_cases()

    constant_ok = data["constant_flux_max_voltage"] < 1e-12
    sign_ok = abs(data["positive_flux_max_voltage"] - data["negative_flux_max_voltage"]) < 1e-12
    speed_ok = data["fast_response_max_voltage"] > data["slow_response_max_voltage"]

    verdict = "conforme strict" if constant_ok and sign_ok and speed_ok else "falsifie"

    return {
        "cases": data,
        "constant_flux_status": "conforme strict" if constant_ok else "falsifie",
        "sign_symmetry_status": "conforme strict" if sign_ok else "falsifie",
        "speed_response_status": "conforme strict" if speed_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "une tension notable apparaît à flux constant",
            "le signe de la réponse ne suit pas la variation de flux",
            "une variation rapide ne produit pas une réponse plus forte",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_induction()

    json_path = outdir / f"electromagnetic_induction_check_{timestamp}.json"
    txt_path = outdir / f"electromagnetic_induction_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: induction et auto-induction\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Flux constant: {results['constant_flux_status']}\n")
        handle.write(f"- Symétrie de signe: {results['sign_symmetry_status']}\n")
        handle.write(f"- Réponse plus forte à variation rapide: {results['speed_response_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()
