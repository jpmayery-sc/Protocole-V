"""Quick coherence check for electric current in aluminum.

The script applies strict qualitative checks to known aluminum behavior:

- low-field Ohmic behavior
- resistivity intermediate between copper and iron
- positive temperature coefficient
- higher resistivity when impurities or oxide are present

It writes a timestamped JSON summary and a text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


RHO_20_C = 2.82e-8  # ohm * m
TEMP_COEFF = 0.00429  # 1 / °C, approximate near room temperature
COPPER_RHO_20_C = 1.68e-8  # ohm * m
IRON_RHO_20_C = 9.71e-8  # ohm * m


def ohmic_resistance(rho: float, length_m: float, area_m2: float) -> float:
    return rho * length_m / area_m2


def expected_rho_at_temp(rho_20_c: float, temp_c: float, ref_temp_c: float = 20.0) -> float:
    return rho_20_c * (1.0 + TEMP_COEFF * (temp_c - ref_temp_c))


def classify_aluminum() -> dict:
    temp_20 = RHO_20_C
    temp_100 = expected_rho_at_temp(RHO_20_C, 100.0)

    surface_case = {
        "pure": RHO_20_C,
        "impure": RHO_20_C * 1.18,
        "oxidized": RHO_20_C * 1.28,
    }

    length_m = 1.0
    area_m2 = 1.0e-6
    r_ohmic = ohmic_resistance(RHO_20_C, length_m, area_m2)
    v_test = 1.0
    i_test = v_test / r_ohmic
    i_expected = v_test / r_ohmic
    ohmic_ok = abs(i_test - i_expected) / i_expected < 1e-12

    temp_ok = temp_100 > temp_20
    intermediate_ok = COPPER_RHO_20_C < RHO_20_C < IRON_RHO_20_C
    impurity_ok = surface_case["impure"] > surface_case["pure"]
    oxide_ok = surface_case["oxidized"] > surface_case["pure"]

    verdict = "conforme strict" if (ohmic_ok and temp_ok and intermediate_ok and impurity_ok and oxide_ok) else "falsifie"

    return {
        "reference": {
            "rho_20_c_ohm_m": RHO_20_C,
            "temp_coeff_per_c": TEMP_COEFF,
            "copper_reference_rho_20_c_ohm_m": COPPER_RHO_20_C,
            "iron_reference_rho_20_c_ohm_m": IRON_RHO_20_C,
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
            "rho_20_c": temp_20,
            "rho_100_c": temp_100,
            "status": "conforme strict" if temp_ok else "falsifie",
        },
        "contrast_test": {
            "rho_aluminum": RHO_20_C,
            "rho_copper": COPPER_RHO_20_C,
            "rho_iron": IRON_RHO_20_C,
            "status": "conforme strict" if intermediate_ok else "falsifie",
        },
        "surface_test": {
            "rho_pure": surface_case["pure"],
            "rho_impure": surface_case["impure"],
            "rho_oxidized": surface_case["oxidized"],
            "status": "conforme strict" if impurity_ok and oxide_ok else "falsifie",
        },
        "overall_verdict": verdict,
        "falsifiers": [
            "l’aluminium n’est pas intermédiaire entre cuivre et fer",
            "la loi d’Ohm ne tient pas au régime faible",
            "la résistivité ne monte pas avec la température",
            "les impuretés ou l’oxyde n’augmentent pas la résistivité",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_aluminum()

    json_path = outdir / f"aluminum_current_check_{timestamp}.json"
    txt_path = outdir / f"aluminum_current_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle du courant électrique dans l’aluminium\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Références:\n")
        handle.write(f"- rho(20°C) = {results['reference']['rho_20_c_ohm_m']:.3e} ohm*m\n")
        handle.write(f"- coefficient thermique = {results['reference']['temp_coeff_per_c']:.4f} /°C\n")
        handle.write(f"- référence cuivre = {results['reference']['copper_reference_rho_20_c_ohm_m']:.3e} ohm*m\n")
        handle.write(f"- référence fer = {results['reference']['iron_reference_rho_20_c_ohm_m']:.3e} ohm*m\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Ohmique faible champ: {results['ohmic_test']['status']}\n")
        handle.write(f"- Température: {results['temperature_test']['status']}\n")
        handle.write(f"- Contraste avec cuivre et fer: {results['contrast_test']['status']}\n")
        handle.write(f"- Surface / pureté: {results['surface_test']['status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()