"""Quick coherence check for strong electromagnetic induction.

The script keeps Faraday's law as the weak-field baseline and then probes a
strong-drive regime where a saturating magnetic response can distort the
induced voltage, create cycle asymmetry, and introduce harmonic content.
It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


MU0 = 4.0 * math.pi * 1e-7
ALPHA = 0.25
H0 = 1.0


def magnetization(h: float) -> float:
    return ALPHA * (h ** 3) / (H0 ** 2 + h ** 2)


def flux_from_drive(t: float, amplitude: float, omega: float) -> float:
    h = amplitude * math.sin(omega * t)
    return h + magnetization(h)


def induced_voltage(t: float, amplitude: float, omega: float) -> float:
    dt = 1.0e-4
    phi_plus = flux_from_drive(t + dt, amplitude, omega)
    phi_minus = flux_from_drive(t - dt, amplitude, omega)
    dphi_dt = (phi_plus - phi_minus) / (2.0 * dt)
    return -dphi_dt


def simulate_case(amplitude: float, omega: float, samples: int = 1200) -> dict:
    max_voltage = 0.0
    max_linear_voltage = 0.0
    max_flux = 0.0
    relative_error_sum = 0.0
    phase_error_samples = 0
    previous_phi = None
    harmonics = []

    for index in range(samples):
        t = index / samples
        h = amplitude * math.sin(omega * t)
        phi = flux_from_drive(t, amplitude, omega)
        voltage = induced_voltage(t, amplitude, omega)
        linear_voltage = -amplitude * omega * math.cos(omega * t)

        max_voltage = max(max_voltage, abs(voltage))
        max_linear_voltage = max(max_linear_voltage, abs(linear_voltage))
        max_flux = max(max_flux, abs(phi))
        relative_error_sum += abs(voltage - linear_voltage) / max(abs(linear_voltage), 1.0e-12)
        phase_error_samples += 1

        if index % 100 == 0:
            harmonics.append({
                "t": t,
                "h": h,
                "phi": phi,
                "voltage": voltage,
            })

        previous_phi = phi

    return {
        "amplitude": amplitude,
        "omega": omega,
        "max_voltage": max_voltage,
        "max_linear_voltage": max_linear_voltage,
        "max_flux": max_flux,
        "mean_relative_error": relative_error_sum / max(phase_error_samples, 1),
        "samples": harmonics,
    }


def classify_strong_induction() -> dict:
    omega = 2.0 * math.pi * 50.0
    weak = simulate_case(amplitude=0.2, omega=omega)
    strong = simulate_case(amplitude=6.0, omega=omega)
    faster = simulate_case(amplitude=6.0, omega=4.0 * omega)

    weak_linear_ok = weak["mean_relative_error"] < 0.05
    strong_distortion_ok = strong["mean_relative_error"] > 0.15
    fast_response_ok = faster["max_voltage"] > strong["max_voltage"]

    verdict = "conforme strict" if weak_linear_ok and strong_distortion_ok and fast_response_ok else "falsifie"

    return {
        "baseline_case": weak,
        "strong_case": strong,
        "fast_strong_case": faster,
        "weak_linear_status": "conforme strict" if weak_linear_ok else "falsifie",
        "strong_distortion_status": "conforme strict" if strong_distortion_ok else "falsifie",
        "fast_response_status": "conforme strict" if fast_response_ok else "falsifie",
        "weak_mean_relative_error": weak["mean_relative_error"],
        "strong_mean_relative_error": strong["mean_relative_error"],
        "fast_mean_relative_error": faster["mean_relative_error"],
        "overall_verdict": verdict,
        "falsifiers": [
            "la réponse reste parfaitement linéaire même à forte excitation",
            "la variation rapide ne change pas l'amplitude induite",
            "le régime fort est indiscernable du régime faible",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_strong_induction()

    json_path = outdir / f"strong_induction_check_{timestamp}.json"
    txt_path = outdir / f"strong_induction_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: induction forte\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Faible excitation quasi linéaire: {results['weak_linear_status']}\n")
        handle.write(f"- Distorsion à forte excitation: {results['strong_distortion_status']}\n")
        handle.write(f"- Réponse plus forte à excitation rapide: {results['fast_response_status']}\n")
        handle.write(f"- Erreur moyenne faible champ: {results['weak_mean_relative_error']:.6f}\n")
        handle.write(f"- Erreur moyenne fort champ: {results['strong_mean_relative_error']:.6f}\n")
        handle.write(f"- Erreur moyenne excitation rapide: {results['fast_mean_relative_error']:.6f}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()