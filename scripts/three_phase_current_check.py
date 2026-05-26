"""Quick coherence check for a balanced three-phase current.

The script verifies a few standard properties of triphasic AC power:

- phases separated by 120 degrees
- current sum close to zero in the balanced case
- nearly constant total power for balanced sinusoidal phases
- visible deviation when one phase is unbalanced
- near-zero neutral current when the system is balanced
- strong neutral current when one phase is lost or strongly weakened

It writes a timestamped JSON summary and a text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path


TWO_PI = 2.0 * math.pi


def phase_wave(amplitude: float, omega_t: float, phase_shift: float) -> float:
    return amplitude * math.sin(omega_t + phase_shift)


def simulate_balanced_case(samples: int = 720):
    amplitude = 10.0
    resistance = 5.0
    max_sum_current = 0.0
    power_values = []

    for index in range(samples):
        omega_t = TWO_PI * index / samples
        ia = phase_wave(amplitude, omega_t, 0.0) / resistance
        ib = phase_wave(amplitude, omega_t, -TWO_PI / 3.0) / resistance
        ic = phase_wave(amplitude, omega_t, -2.0 * TWO_PI / 3.0) / resistance
        current_sum = ia + ib + ic
        max_sum_current = max(max_sum_current, abs(current_sum))
        power_values.append((ia ** 2 + ib ** 2 + ic ** 2) * resistance)

    p_min = min(power_values)
    p_max = max(power_values)
    p_mean = sum(power_values) / len(power_values)
    power_span = p_max - p_min

    return {
        "max_abs_current_sum": max_sum_current,
        "power_mean": p_mean,
        "power_min": p_min,
        "power_max": p_max,
        "power_span": power_span,
    }


def simulate_unbalanced_case(samples: int = 720):
    amplitudes = (10.0, 10.0, 7.5)
    resistance = 5.0
    max_sum_current = 0.0
    power_values = []

    for index in range(samples):
        omega_t = TWO_PI * index / samples
        ia = phase_wave(amplitudes[0], omega_t, 0.0) / resistance
        ib = phase_wave(amplitudes[1], omega_t, -TWO_PI / 3.0) / resistance
        ic = phase_wave(amplitudes[2], omega_t, -2.0 * TWO_PI / 3.0) / resistance
        current_sum = ia + ib + ic
        max_sum_current = max(max_sum_current, abs(current_sum))
        power_values.append((ia ** 2 + ib ** 2 + ic ** 2) * resistance)

    p_min = min(power_values)
    p_max = max(power_values)
    p_mean = sum(power_values) / len(power_values)
    power_span = p_max - p_min

    return {
        "max_abs_current_sum": max_sum_current,
        "power_mean": p_mean,
        "power_min": p_min,
        "power_max": p_max,
        "power_span": power_span,
    }


def simulate_neutral_case(samples: int = 720):
    """Return balanced and defective neutral currents for a four-wire system."""
    balanced = []
    defective = []
    resistance = 5.0

    for index in range(samples):
        omega_t = TWO_PI * index / samples

        # Balanced three-phase set
        ia = phase_wave(10.0, omega_t, 0.0) / resistance
        ib = phase_wave(10.0, omega_t, -TWO_PI / 3.0) / resistance
        ic = phase_wave(10.0, omega_t, -2.0 * TWO_PI / 3.0) / resistance
        balanced.append(abs(ia + ib + ic))

        # Defect: one phase strongly weakened
        ia_d = phase_wave(10.0, omega_t, 0.0) / resistance
        ib_d = phase_wave(10.0, omega_t, -TWO_PI / 3.0) / resistance
        ic_d = phase_wave(4.0, omega_t, -2.0 * TWO_PI / 3.0) / resistance
        defective.append(abs(ia_d + ib_d + ic_d))

    return {
        "balanced_neutral_max": max(balanced),
        "balanced_neutral_mean": sum(balanced) / len(balanced),
        "defective_neutral_max": max(defective),
        "defective_neutral_mean": sum(defective) / len(defective),
    }


def classify_three_phase() -> dict:
    balanced = simulate_balanced_case()
    unbalanced = simulate_unbalanced_case()
    neutral = simulate_neutral_case()

    balanced_current_ok = balanced["max_abs_current_sum"] < 1e-12
    balanced_power_ok = balanced["power_span"] < 1e-10
    unbalanced_current_ok = unbalanced["max_abs_current_sum"] > 0.1
    unbalanced_power_ok = unbalanced["power_span"] > balanced["power_span"]
    neutral_balanced_ok = neutral["balanced_neutral_max"] < 1e-12
    neutral_defect_ok = neutral["defective_neutral_max"] > 0.1

    verdict = (
        "conforme strict"
        if balanced_current_ok
        and balanced_power_ok
        and unbalanced_current_ok
        and unbalanced_power_ok
        and neutral_balanced_ok
        and neutral_defect_ok
        else "falsifie"
    )

    return {
        "balanced_case": balanced,
        "unbalanced_case": unbalanced,
        "neutral_case": neutral,
        "balanced_current_status": "conforme strict" if balanced_current_ok else "falsifie",
        "balanced_power_status": "conforme strict" if balanced_power_ok else "falsifie",
        "unbalanced_current_status": "conforme strict" if unbalanced_current_ok else "falsifie",
        "unbalanced_power_status": "conforme strict" if unbalanced_power_ok else "falsifie",
        "neutral_balanced_status": "conforme strict" if neutral_balanced_ok else "falsifie",
        "neutral_defect_status": "conforme strict" if neutral_defect_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "les trois phases ne sont pas séparées correctement",
            "la somme des courants ne s’annule pas en équilibre",
            "la puissance totale varie trop en régime équilibré",
            "un déséquilibre ne crée aucun écart mesurable",
            "le neutre reste nul alors qu’une phase est affaiblie",
            "une phase coupée ou très faible ne laisse aucune signature sur le neutre",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_three_phase()

    json_path = outdir / f"three_phase_current_check_{timestamp}.json"
    txt_path = outdir / f"three_phase_current_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle du courant triphasé\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Équilibre des courants: {results['balanced_current_status']}\n")
        handle.write(f"- Puissance équilibrée: {results['balanced_power_status']}\n")
        handle.write(f"- Déséquilibre du courant: {results['unbalanced_current_status']}\n")
        handle.write(f"- Réponse en puissance au déséquilibre: {results['unbalanced_power_status']}\n\n")
        handle.write(f"- Neutre en équilibre: {results['neutral_balanced_status']}\n")
        handle.write(f"- Neutre en défaut: {results['neutral_defect_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()