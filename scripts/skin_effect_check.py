"""Quick coherence check for the electromagnetic skin effect.

The script evaluates the standard skin depth relation and compares low and
high frequency behavior. It writes a timestamped JSON summary and a short
text report under results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


RHO = 1.68e-8  # ohm * m (copper reference)
MU0 = 4.0 * math.pi * 1e-7  # H/m


def skin_depth(rho: float, mu: float, omega: float) -> float:
    return math.sqrt(2.0 * rho / (mu * omega))


def classify_skin_effect() -> dict:
    low_omega = 2.0 * math.pi * 50.0
    high_omega = 2.0 * math.pi * 50_000.0

    delta_low = skin_depth(RHO, MU0, low_omega)
    delta_high = skin_depth(RHO, MU0, high_omega)
    higher_rho = skin_depth(RHO * 2.0, MU0, high_omega)
    higher_mu = skin_depth(RHO, MU0 * 10.0, high_omega)

    low_high_ok = delta_high < delta_low
    rho_ok = higher_rho > delta_high
    mu_ok = higher_mu < delta_high

    verdict = "conforme strict" if low_high_ok and rho_ok and mu_ok else "falsifie"

    return {
        "delta_low_m": delta_low,
        "delta_high_m": delta_high,
        "delta_high_higher_rho_m": higher_rho,
        "delta_high_higher_mu_m": higher_mu,
        "low_high_status": "conforme strict" if low_high_ok else "falsifie",
        "rho_status": "conforme strict" if rho_ok else "falsifie",
        "mu_status": "conforme strict" if mu_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "la profondeur de peau ne diminue pas quand la fréquence augmente",
            "une résistivité plus grande ne change pas la profondeur de peau",
            "une perméabilité plus grande ne réduit pas la profondeur de peau",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_skin_effect()

    json_path = outdir / f"skin_effect_check_{timestamp}.json"
    txt_path = outdir / f"skin_effect_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: effet peau\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Basse fréquence vs haute fréquence: {results['low_high_status']}\n")
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
