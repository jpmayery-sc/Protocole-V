"""Quick coherence check for strong skin effect.

The script compares a low-frequency regime where current penetration stays
large with a strong high-frequency regime where the skin depth should shrink
and a nonlinear material correction can amplify the confinement. It writes a
timestamped JSON summary and a short text report under results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


RHO = 1.68e-8
MU0 = 4.0 * math.pi * 1e-7
ALPHA = 0.15


def skin_depth(rho: float, mu: float, omega: float) -> float:
    return math.sqrt(2.0 * rho / (mu * omega))


def corrected_skin_depth(rho: float, mu: float, omega: float) -> float:
    base = skin_depth(rho, mu, omega)
    nonlinear_factor = 1.0 + ALPHA * math.log10(max(omega / (2.0 * math.pi * 50.0), 1.0))
    return base / nonlinear_factor


def classify_strong_skin_effect() -> dict:
    low_omega = 2.0 * math.pi * 50.0
    strong_omega = 2.0 * math.pi * 500_000.0

    low_depth = skin_depth(RHO, MU0, low_omega)
    strong_depth = skin_depth(RHO, MU0, strong_omega)
    corrected_depth = corrected_skin_depth(RHO, MU0, strong_omega)
    higher_rho_depth = corrected_skin_depth(RHO * 2.0, MU0, strong_omega)
    higher_mu_depth = corrected_skin_depth(RHO, MU0 * 10.0, strong_omega)

    low_high_ok = strong_depth < low_depth
    correction_ok = corrected_depth < strong_depth * 0.95
    rho_ok = higher_rho_depth > corrected_depth
    mu_ok = higher_mu_depth < corrected_depth

    verdict = "conforme strict" if low_high_ok and correction_ok and rho_ok and mu_ok else "falsifie"

    return {
        "low_frequency_depth_m": low_depth,
        "strong_frequency_depth_m": strong_depth,
        "corrected_strong_depth_m": corrected_depth,
        "strong_depth_higher_rho_m": higher_rho_depth,
        "strong_depth_higher_mu_m": higher_mu_depth,
        "low_high_status": "conforme strict" if low_high_ok else "falsifie",
        "correction_status": "conforme strict" if correction_ok else "falsifie",
        "rho_status": "conforme strict" if rho_ok else "falsifie",
        "mu_status": "conforme strict" if mu_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "la profondeur de peau ne diminue pas quand la fréquence augmente",
            "la correction forte ne resserre pas davantage le courant",
            "une résistivité plus grande ne change pas la profondeur de peau corrigée",
            "une perméabilité plus grande ne réduit pas la profondeur de peau corrigée",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_strong_skin_effect()

    json_path = outdir / f"strong_skin_effect_check_{timestamp}.json"
    txt_path = outdir / f"strong_skin_effect_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: effet peau fort\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Basse fréquence vs haute fréquence: {results['low_high_status']}\n")
        handle.write(f"- Correction non linéaire à forte fréquence: {results['correction_status']}\n")
        handle.write(f"- Résistivité plus grande: {results['rho_status']}\n")
        handle.write(f"- Perméabilité plus grande: {results['mu_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()