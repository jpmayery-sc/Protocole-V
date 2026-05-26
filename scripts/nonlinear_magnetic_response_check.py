"""Quick coherence check for nonlinear magnetic response.

The script uses a simple saturating magnetization model to verify that the
response is approximately linear at low field and saturates at high field.
It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


MS = 1.0
H0 = 2.0


def magnetization(h: float) -> float:
    return MS * math.tanh(h / H0)


def classify_nonlinear_response() -> dict:
    low_h = [0.0, 0.1, 0.2]
    high_h = [0.0, 3.0, 6.0]

    low_values = [magnetization(h) for h in low_h]
    high_values = [magnetization(h) for h in high_h]

    low_linear_ok = abs(low_values[2] - 2.0 * low_values[1]) < 0.02
    high_saturation_ok = high_values[-1] > 0.9 * MS
    curve_ok = high_values[-1] - high_values[1] < 0.4 * MS

    verdict = "conforme strict" if low_linear_ok and high_saturation_ok and curve_ok else "falsifie"

    return {
        "low_field_values": low_values,
        "high_field_values": high_values,
        "low_linear_status": "conforme strict" if low_linear_ok else "falsifie",
        "high_saturation_status": "conforme strict" if high_saturation_ok else "falsifie",
        "curve_status": "conforme strict" if curve_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "la réponse reste linéaire jusqu’à fort champ",
            "la saturation n’apparaît pas",
            "un matériau magnétique ne se distingue pas d’un matériau non magnétique",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_nonlinear_response()

    json_path = outdir / f"nonlinear_magnetic_response_check_{timestamp}.json"
    txt_path = outdir / f"nonlinear_magnetic_response_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle électromagnétique: réponse non linéaire magnétique\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Faible champ quasi linéaire: {results['low_linear_status']}\n")
        handle.write(f"- Saturation à champ fort: {results['high_saturation_status']}\n")
        handle.write(f"- Courbure de la réponse: {results['curve_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()