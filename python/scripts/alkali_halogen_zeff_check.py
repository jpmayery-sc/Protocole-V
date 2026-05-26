"""Validate simple Z_eff and screening monotonicity on alkali, halogen, pnictogen, chalcogen, noble gas, and alkaline earth families.

The script uses first ionization energies as a hydrogenic proxy:
Z_eff = sqrt(I * n^2 / R_H).
It checks that both Z_eff and screening S = Z - Z_eff remain monotonic inside
each family.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


R_H_EV = 13.6

FAMILIES = {
    "alkali": [
        {"symbol": "Li", "Z": 3, "n": 2, "ionization_ev": 5.3917},
        {"symbol": "Na", "Z": 11, "n": 3, "ionization_ev": 5.1391},
        {"symbol": "K", "Z": 19, "n": 4, "ionization_ev": 4.3407},
        {"symbol": "Rb", "Z": 37, "n": 5, "ionization_ev": 4.1771},
        {"symbol": "Cs", "Z": 55, "n": 6, "ionization_ev": 3.8939},
    ],
    "halogen": [
        {"symbol": "F", "Z": 9, "n": 2, "ionization_ev": 17.4228},
        {"symbol": "Cl", "Z": 17, "n": 3, "ionization_ev": 12.9676},
        {"symbol": "Br", "Z": 35, "n": 4, "ionization_ev": 11.8138},
        {"symbol": "I", "Z": 53, "n": 5, "ionization_ev": 10.4513},
    ],
    "pnictogen": [
        {"symbol": "N", "Z": 7, "n": 2, "ionization_ev": 14.5341},
        {"symbol": "P", "Z": 15, "n": 3, "ionization_ev": 10.4867},
        {"symbol": "As", "Z": 33, "n": 4, "ionization_ev": 9.8152},
        {"symbol": "Sb", "Z": 51, "n": 5, "ionization_ev": 8.6084},
        {"symbol": "Bi", "Z": 83, "n": 6, "ionization_ev": 7.2856},
    ],
    "chalcogen": [
        {"symbol": "O", "Z": 8, "n": 2, "ionization_ev": 13.6181},
        {"symbol": "S", "Z": 16, "n": 3, "ionization_ev": 10.36},
        {"symbol": "Se", "Z": 34, "n": 4, "ionization_ev": 9.7524},
        {"symbol": "Te", "Z": 52, "n": 5, "ionization_ev": 9.0096},
        {"symbol": "Po", "Z": 84, "n": 6, "ionization_ev": 8.4167},
    ],
    "noble_gas": [
        {"symbol": "He", "Z": 2, "n": 1, "ionization_ev": 24.59},
        {"symbol": "Ne", "Z": 10, "n": 2, "ionization_ev": 21.56},
        {"symbol": "Ar", "Z": 18, "n": 3, "ionization_ev": 15.76},
        {"symbol": "Kr", "Z": 36, "n": 4, "ionization_ev": 14.00},
        {"symbol": "Xe", "Z": 54, "n": 5, "ionization_ev": 12.13},
    ],
    "alkaline_earth": [
        {"symbol": "Be", "Z": 4, "n": 2, "ionization_ev": 9.32},
        {"symbol": "Mg", "Z": 12, "n": 3, "ionization_ev": 7.65},
        {"symbol": "Ca", "Z": 20, "n": 4, "ionization_ev": 6.1132},
        {"symbol": "Sr", "Z": 38, "n": 5, "ionization_ev": 5.6949},
        {"symbol": "Ba", "Z": 56, "n": 6, "ionization_ev": 5.2117},
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def is_monotonic_increasing(values: list[float]) -> bool:
    return all(later > earlier for earlier, later in zip(values, values[1:]))


def evaluate_family(name: str, cases: list[dict]) -> dict:
    evaluated = []
    zeff_values = []
    screening_values = []

    for case in cases:
        zeff = estimate_zeff(case["ionization_ev"], int(case["n"]))
        screening = float(case["Z"]) - zeff
        zeff_values.append(zeff)
        screening_values.append(screening)
        evaluated.append(
            {
                **case,
                "zeff": round(zeff, 6),
                "screening": round(screening, 6),
            }
        )

    zeff_ok = is_monotonic_increasing(zeff_values)
    screening_ok = is_monotonic_increasing(screening_values)
    family_ok = zeff_ok and screening_ok

    return {
        "family": name,
        "supported": family_ok,
        "zeff_monotonic": zeff_ok,
        "screening_monotonic": screening_ok,
        "cases": evaluated,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    family_results = {name: evaluate_family(name, cases) for name, cases in FAMILIES.items()}
    verdict = "supported" if all(result["supported"] for result in family_results.values()) else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "family_results": family_results,
    }

    json_path = outdir / f"alkali_halogen_zeff_check_{ts}.json"
    report_path = outdir / f"alkali_halogen_zeff_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alkali, halogen, and pnictogen Z_eff check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        "",
    ]
    for family_name, result in family_results.items():
        lines.append(f"{family_name}:")
        lines.append(f"- zeff_monotonic: {result['zeff_monotonic']}")
        lines.append(f"- screening_monotonic: {result['screening_monotonic']}")
        for case in result["cases"]:
            lines.append(
                f"  - {case['symbol']}: Z={case['Z']} n={case['n']} I={case['ionization_ev']:.4f} Zeff={case['zeff']:.6f} S={case['screening']:.6f}"
            )
        lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["report_path"] = str(report_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()