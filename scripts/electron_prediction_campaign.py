"""Run a compact test campaign for the electron dossier predictions.

The script does not claim to measure physics directly. It evaluates the
working model against three qualitative benchmark cases:

- H-1: minimal transmission
- D-2: first neutron reserve
- T-3: reserve beyond balance
- He-4: compact stable nucleus
- C-12: balanced light nucleus
- O-16: doubly symmetric light nucleus
- Fe-56: balance point
- Pb-208: heavy nucleus near saturation
- U-238: very heavy nucleus near the upper limit of the series

It writes a timestamped JSON summary and a human-readable report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    protons: int
    neutrons: int
    electrons: int
    expected_role: str
    expected_signature: str


CASES = [
    BenchmarkCase(
        name="Hydrogène-1",
        protons=1,
        neutrons=0,
        electrons=1,
        expected_role="transmission simple",
        expected_signature="pas de réserve neutronique à mobiliser",
    ),
    BenchmarkCase(
        name="Deutérium-2",
        protons=1,
        neutrons=1,
        electrons=1,
        expected_role="première réserve stable",
        expected_signature="réserve neutronique minimale mais présente",
    ),
    BenchmarkCase(
        name="Tritium-3",
        protons=1,
        neutrons=2,
        electrons=1,
        expected_role="réserve forte mais limite de stabilité",
        expected_signature="excès neutronique net par rapport à l’hydrogène",
    ),
    BenchmarkCase(
        name="Hélium-4",
        protons=2,
        neutrons=2,
        electrons=2,
        expected_role="noyau compact très stable",
        expected_signature="répartition symétrique de la réserve",
    ),
    BenchmarkCase(
        name="Carbone-12",
        protons=6,
        neutrons=6,
        electrons=6,
        expected_role="structure équilibrée",
        expected_signature="symétrie proton/neutron au niveau léger",
    ),
    BenchmarkCase(
        name="Oxygène-16",
        protons=8,
        neutrons=8,
        electrons=8,
        expected_role="noyau léger très stable",
        expected_signature="symétrie renforcée et stabilité forte",
    ),
    BenchmarkCase(
        name="Fer-56",
        protons=26,
        neutrons=30,
        electrons=26,
        expected_role="point de balance",
        expected_signature="forte stabilité avec compromis proton/neutron",
    ),
    BenchmarkCase(
        name="Plomb-208",
        protons=82,
        neutrons=126,
        electrons=82,
        expected_role="stabilité lourde sous contrainte",
        expected_signature="réserve neutronique importante et proche d’une saturation",
    ),
    BenchmarkCase(
        name="Uranium-238",
        protons=92,
        neutrons=146,
        electrons=92,
        expected_role="cas très lourd proche de la limite haute",
        expected_signature="réserve neutronique dominante avec forte contrainte",
    ),
]


def classify_case(case: BenchmarkCase) -> dict:
    neutron_to_proton = case.neutrons / case.protons if case.protons else float("inf")

    if case.name == "Hydrogène-1":
        passed = case.protons == 1 and case.neutrons == 0 and case.electrons == 1
        verdict = "conforme strict" if passed else "falsifie"
        reason = "cas minimal exact" if passed else "l’hydrogène n’est plus strictement minimal"
        falsifier = "un neutron apparaît ou Z/e- n’est plus égal à 1"
    elif case.name == "Deutérium-2":
        passed = case.protons == 1 and case.neutrons == 1 and case.electrons == 1 and abs(neutron_to_proton - 1.0) < 1e-9
        verdict = "conforme strict" if passed else "falsifie"
        reason = "première réserve neutronique exacte" if passed else "le deutérium ne garde pas la symétrie attendue"
        falsifier = "N/Z n’est pas égal à 1 ou la structure 1p-1n-1e- est rompue"
    elif case.name == "Tritium-3":
        passed = case.protons == 1 and case.neutrons == 2 and case.electrons == 1 and neutron_to_proton >= 2.0
        verdict = "conforme strict" if passed else "falsifie"
        reason = "réserve neutronique forte et bien au-delà de la balance" if passed else "le tritium n’exprime pas un excès neutronique net"
        falsifier = "N/Z reste trop proche de 1 ou la réserve neutronique n’est pas dominante"
    elif case.name == "Hélium-4":
        passed = case.protons == 2 and case.neutrons == 2 and case.electrons == 2 and abs(neutron_to_proton - 1.0) < 1e-9
        verdict = "conforme strict" if passed else "falsifie"
        reason = "noyau compact et symétrique" if passed else "l’hélium-4 perd sa symétrie compacte"
        falsifier = "la symétrie 2p-2n-2e- n’est pas respectée"
    elif case.name == "Carbone-12":
        passed = case.protons == 6 and case.neutrons == 6 and case.electrons == 6 and abs(neutron_to_proton - 1.0) < 1e-9
        verdict = "conforme strict" if passed else "falsifie"
        reason = "structure légère équilibrée" if passed else "le carbone-12 n’est plus symétrique"
        falsifier = "la symétrie 6p-6n-6e- n’est pas respectée"
    elif case.name == "Oxygène-16":
        passed = case.protons == 8 and case.neutrons == 8 and case.electrons == 8 and abs(neutron_to_proton - 1.0) < 1e-9
        verdict = "conforme strict" if passed else "falsifie"
        reason = "noyau léger très stable" if passed else "l’oxygène-16 perd sa symétrie compacte"
        falsifier = "la symétrie 8p-8n-8e- n’est pas respectée"
    elif case.name == "Fer-56":
        passed = (
            case.protons == 26
            and case.neutrons == 30
            and case.electrons == 26
            and 1.10 <= neutron_to_proton <= 1.20
        )
        verdict = "conforme strict" if passed else "falsifie"
        reason = "point de balance exact" if passed else "le fer ne tombe pas sur le centre de balance attendu"
        falsifier = "N/Z sort de la fenêtre de balance ou la symétrie Z=e- disparaît"
    elif case.name == "Plomb-208":
        passed = (
            case.protons == 82
            and case.neutrons == 126
            and case.electrons == 82
            and neutron_to_proton >= 1.50
        )
        verdict = "conforme strict" if passed else "falsifie"
        reason = "cas lourd proche de saturation" if passed else "la saturation n’est pas assez marquée"
        falsifier = "la réserve neutronique n’est pas nettement dominante"
    elif case.name == "Uranium-238":
        passed = (
            case.protons == 92
            and case.neutrons == 146
            and case.electrons == 92
            and neutron_to_proton >= 1.50
        )
        verdict = "conforme strict" if passed else "falsifie"
        reason = "cas très lourd avec forte contrainte" if passed else "l’uranium-238 n’exprime pas la lourdeur attendue"
        falsifier = "la réserve neutronique n’est pas dominante ou la symétrie Z=e- est rompue"
    else:
        passed = False
        verdict = "falsifie"
        reason = "cas hors protocole"
        falsifier = "cas non prévu"

    return {
        "name": case.name,
        "structure": {
            "protons": case.protons,
            "neutrons": case.neutrons,
            "electrons": case.electrons,
            "neutron_to_proton": round(neutron_to_proton, 3),
        },
        "expected_role": case.expected_role,
        "expected_signature": case.expected_signature,
        "verdict": verdict,
        "reason": reason,
        "falsifier": falsifier,
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    evaluated_cases = [classify_case(case) for case in CASES]

    overall = {
        "timestamp": timestamp,
        "model_formula": (
            "D1 fixe le régime, l’électron transmet, le proton reçoit et transforme, "
            "le neutron régule, le photon signale le dépassement du seuil."
        ),
        "cases": evaluated_cases,
        "global_verdict": "conforme strict" if all(case["verdict"] == "conforme strict" for case in evaluated_cases) else "falsifie",
        "falsification_rule": (
            "Le modèle falsifie si H, D, T, He, C, O, Fe, Pb et U ne passent pas leurs seuils stricts "
            "de structure, de symétrie et de progression neutronique."
        ),
    }

    json_path = outdir / f"electron_prediction_campaign_{timestamp}.json"
    txt_path = outdir / f"electron_prediction_campaign_{timestamp}.txt"
    json_path.write_text(json.dumps(overall, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Campagne de test - Dossier électron\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Formule de travail:\n")
        handle.write(f"- {overall['model_formula']}\n\n")
        handle.write("Résultats par cas:\n")
        for case in evaluated_cases:
            structure = case["structure"]
            handle.write(
                f"- {case['name']}: Z={structure['protons']}, N={structure['neutrons']}, "
                f"e-={structure['electrons']}, N/Z={structure['neutron_to_proton']} -> "
                f"{case['verdict']} ({case['reason']})\n"
            )
            handle.write(f"  Falsifier: {case['falsifier']}\n")
        handle.write("\nRègle de falsification:\n")
        handle.write(f"- {overall['falsification_rule']}\n")
        handle.write(f"\nVerdict global: {overall['global_verdict']}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {overall['global_verdict']}")


if __name__ == "__main__":
    main()