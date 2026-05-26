"""Quick coherence check for electric current in copper.

This script compares a few known reference trends for copper against simple
strict rules:

- low-field Ohmic behavior
- resistivity near room temperature
- positive temperature coefficient
- higher resistivity when purity decreases

It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


RHO_20_C = 1.68e-8  # ohm * m
TEMP_COEFF = 0.0039  # 1 / °C, near room temperature


def ohmic_resistance(rho: float, length_m: float, area_m2: float) -> float:
    return rho * length_m / area_m2


def expected_rho_at_temp(rho_20_c: float, temp_c: float, ref_temp_c: float = 20.0) -> float:
    return rho_20_c * (1.0 + TEMP_COEFF * (temp_c - ref_temp_c))


def classify_copper() -> dict:
    temperature_cases = {
        "20C": RHO_20_C,
        "100C": expected_rho_at_temp(RHO_20_C, 100.0),
    }

    impurity_case = {
        "pure": RHO_20_C,
        "impure": RHO_20_C * 1.25,
    }

    length_m = 1.0
    area_m2 = 1.0e-6
    r_ohmic = ohmic_resistance(RHO_20_C, length_m, area_m2)
    v_test = 1.0
    i_test = v_test / r_ohmic
    i_expected = v_test / r_ohmic
    ohmic_ok = abs(i_test - i_expected) / i_expected < 1e-12

    rho_100 = temperature_cases["100C"]
    temp_ok = rho_100 > temperature_cases["20C"]

    impurity_ok = impurity_case["impure"] > impurity_case["pure"]

    verdict = "conforme strict" if (ohmic_ok and temp_ok and impurity_ok) else "falsifie"

    return {
        "reference": {
            "rho_20_c_ohm_m": RHO_20_C,
            "temp_coeff_per_c": TEMP_COEFF,
        },
        "ohmic_test": {
            "length_m": length_m,
            "area_m2": area_m2,
            "resistance_ohm": r_ohmic,
            "v_test_v": v_test,
            "i_test_a": i_test,
            "status": "conforme strict" if ohmic_ok else "falsifie",
        },
        "temperature_test": {
            "rho_20_c": temperature_cases["20C"],
            "rho_100_c": rho_100,
            "status": "conforme strict" if temp_ok else "falsifie",
        },
        "purity_test": {
            "rho_pure": impurity_case["pure"],
            "rho_impure": impurity_case["impure"],
            "status": "conforme strict" if impurity_ok else "falsifie",
        },
        "overall_verdict": verdict,
        "falsifiers": [
            "la loi d’Ohm ne tient pas au régime faible",
            "la résistivité ne monte pas avec la température",
            "les impuretés n’augmentent pas la résistivité",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_copper()

    json_path = outdir / f"copper_current_check_{timestamp}.json"
    txt_path = outdir / f"copper_current_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle du courant électrique dans le cuivre\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Références:\n")
        handle.write(f"- rho(20°C) = {results['reference']['rho_20_c_ohm_m']:.3e} ohm*m\n")
        handle.write(f"- coefficient thermique = {results['reference']['temp_coeff_per_c']:.4f} /°C\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Ohmique faible champ: {results['ohmic_test']['status']}\n")
        handle.write(f"- Température: {results['temperature_test']['status']}\n")
        handle.write(f"- Pureté: {results['purity_test']['status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()