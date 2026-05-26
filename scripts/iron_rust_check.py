"""Quick coherence check for iron rusting and oxidation.

The script verifies the dossier rule used for rust:

- iron keeps the same proton count during corrosion
- oxidation changes the electron count / oxidation state
- rust corresponds to a chemical transformation, not a nuclear one

It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


CASES = [
    {
        "label": "iron_metal",
        "symbol": "Fe",
        "protons": 26,
        "electrons": 26,
        "oxidation_state": 0,
        "kind": "reference",
    },
    {
        "label": "iron_two_plus",
        "symbol": "Fe2+",
        "protons": 26,
        "electrons": 24,
        "oxidation_state": 2,
        "kind": "oxidized",
    },
    {
        "label": "iron_three_plus",
        "symbol": "Fe3+",
        "protons": 26,
        "electrons": 23,
        "oxidation_state": 3,
        "kind": "oxidized",
    },
    {
        "label": "rust_fe2o3",
        "symbol": "Fe2O3",
        "protons": 26,
        "electrons": 23,
        "oxidation_state": 3,
        "kind": "rust",
    },
]


def classify_rust() -> dict:
    evaluated = []
    nucleus_ok = True
    oxidation_ok = True

    reference = CASES[0]
    reference_electrons = reference["electrons"]

    for case in CASES:
        protons = case["protons"]
        electrons = case["electrons"]
        same_nucleus = protons == reference["protons"]
        oxidation_change = electrons < reference_electrons if case["kind"] != "reference" else electrons == reference_electrons

        if case["kind"] == "reference":
            nucleus_ok = nucleus_ok and same_nucleus and electrons == reference_electrons
            status = "conforme strict" if same_nucleus and electrons == reference_electrons else "falsifie"
        else:
            nucleus_ok = nucleus_ok and same_nucleus
            oxidation_ok = oxidation_ok and oxidation_change
            status = "conforme strict" if same_nucleus and oxidation_change else "falsifie"

        evaluated.append({
            **case,
            "charge": protons - electrons,
            "same_nucleus_as_reference": same_nucleus,
            "status": status,
        })

    verdict = "conforme strict" if nucleus_ok and oxidation_ok else "falsifie"

    return {
        "cases": evaluated,
        "nucleus_rule_status": "conforme strict" if nucleus_ok else "falsifie",
        "oxidation_rule_status": "conforme strict" if oxidation_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "la corrosion change le nombre de protons du fer",
            "la rouille ne s’accompagne d’aucune variation électronique",
            "le fer oxydé n’est plus chimiquement du fer alors que le noyau reste identique",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_rust()

    json_path = outdir / f"iron_rust_check_{timestamp}.json"
    txt_path = outdir / f"iron_rust_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle de la rouille du fer\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        for case in results["cases"]:
            handle.write(
                f"- {case['label']} ({case['symbol']}): {case['status']} "
                f"(N_p={case['protons']}, N_e={case['electrons']}, charge={case['charge']}, O={case['oxidation_state']})\n"
            )
        handle.write(f"\nVerdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()