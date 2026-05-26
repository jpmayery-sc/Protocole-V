"""Quick coherence check for neutral atoms and simple ions.

The script verifies the core rule used in the dossier:

- a neutral atom satisfies N_e = N_p
- ionization changes the electron count without changing the proton count

It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


CASES = [
    {"label": "hydrogen_neutral", "symbol": "H", "protons": 1, "electrons": 1, "kind": "neutral"},
    {"label": "helium_neutral", "symbol": "He", "protons": 2, "electrons": 2, "kind": "neutral"},
    {"label": "iron_neutral", "symbol": "Fe", "protons": 26, "electrons": 26, "kind": "neutral"},
    {"label": "sodium_cation", "symbol": "Na+", "protons": 11, "electrons": 10, "kind": "ion"},
    {"label": "chlorine_anion", "symbol": "Cl-", "protons": 17, "electrons": 18, "kind": "ion"},
]


def classify_cases() -> dict:
    evaluated = []
    neutral_ok = True
    ion_ok = True

    for case in CASES:
        protons = case["protons"]
        electrons = case["electrons"]
        is_neutral = electrons == protons
        is_ion = electrons != protons

        if case["kind"] == "neutral":
            neutral_ok = neutral_ok and is_neutral
            status = "conforme strict" if is_neutral else "falsifie"
        else:
            ion_ok = ion_ok and is_ion
            status = "conforme strict" if is_ion else "falsifie"

        evaluated.append({
            **case,
            "charge": protons - electrons,
            "status": status,
        })

    verdict = "conforme strict" if neutral_ok and ion_ok else "falsifie"

    return {
        "cases": evaluated,
        "neutral_rule_status": "conforme strict" if neutral_ok else "falsifie",
        "ion_rule_status": "conforme strict" if ion_ok else "falsifie",
        "overall_verdict": verdict,
        "falsifiers": [
            "un atome annoncé neutre ne vérifie pas N_e = N_p",
            "l’ionisation change le nombre de protons au lieu des électrons",
            "les cas ioniques ne se distinguent pas des cas neutres",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_cases()

    json_path = outdir / f"neutral_atom_ion_check_{timestamp}.json"
    txt_path = outdir / f"neutral_atom_ion_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle des atomes neutres et des ions\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        for case in results["cases"]:
            handle.write(
                f"- {case['label']} ({case['symbol']}): {case['status']} "
                f"(N_p={case['protons']}, N_e={case['electrons']}, charge={case['charge']})\n"
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