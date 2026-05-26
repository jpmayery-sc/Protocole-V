"""Quick coherence check for strong nonlinear magnetic saturation.

The script keeps the same saturating family as the standard nonlinear magnetic
response check, but pushes the field farther to verify that low-field behavior
remains linear while the strong-field regime clearly saturates. It writes a
timestamped JSON summary and a short text report under results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


MS = 1.0
H0 = 1.2


def magnetization(h: float) -> float:
    return MS * math.tanh(h / H0)


def classify_strong_nonlinear_response() -> dict:
    low_h = [0.0, 0.05, 0.1]
    medium_h = [0.0, 1.5, 3.0]
    strong_h = [0.0, 6.0, 12.0]

    low_values = [magnetization(h) for h in low_h]
    medium_values = [magnetization(h) for h in medium_h]
    strong_values = [magnetization(h) for h in strong_h]

    low_linear_ok = abs(low_values[2] - 2.0 * low_values[1]) < 0.015
    medium_curve_ok = medium_values[-1] - medium_values[1] < 0.5 * MS
    strong_saturation_ok = strong_values[-1] > 0.97 * MS
    strong_plateau_ok = strong_values[-1] - strong_values[1] < 0.15 * MS

    verdict = "conforme strict" if low_linear_ok and medium_curve_ok and strong_saturation_ok and strong_plateau_ok else "falsifie"

    return {
        "low_field_values": low_values,
        "medium_field_values": medium_values,
        "strong_field_values": strong_values,
        "low_linear_status": "conforme strict" if low_linear_ok else "falsifie",
        "medium_curve_status": "conforme strict" if medium_curve_ok else "falsifie",
        "strong_saturation_status": "conforme strict" if strong_saturation_ok else "falsifie",
        "strong_plateau_status": "conforme strict" if strong_plateau_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "la réponse reste linéaire à fort champ",
            "la saturation ne se rapproche pas d’un plateau",
            "la réponse forte ne se distingue pas du régime faible",
            "le matériau magnétique ne montre pas de courbure supplémentaire",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_strong_nonlinear_response()

    json_path = outdir / f"strong_nonlinear_magnetic_response_check_{timestamp}.json"
    txt_path = outdir / f"strong_nonlinear_magnetic_response_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: saturation magnétique forte\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Faible champ quasi linéaire: {results['low_linear_status']}\n")
        handle.write(f"- Courbure au champ intermédiaire: {results['medium_curve_status']}\n")
        handle.write(f"- Saturation au champ fort: {results['strong_saturation_status']}\n")
        handle.write(f"- Plateau au champ fort: {results['strong_plateau_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()