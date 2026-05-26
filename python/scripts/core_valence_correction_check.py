"""Check whether an explicit core/valence correction improves radius fits.

The check formalizes the candidate correction with explicit variables:

    radius ~ intercept + alpha * Z_eff + beta * l_valence + gamma * l_core

The goal is not to claim a universal law, but to see whether adding the
core/valence descriptors reduces residuals across representative families.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6

FAMILIES = {
    "alkali": {
        "l_valence": 0,
        "l_core": 0,
        "items": [
            {"symbol": "Li", "period": 2, "mass_u": 6.94, "radius_pm": 152.0, "ionization_ev": 5.3917},
            {"symbol": "Na", "period": 3, "mass_u": 22.98976928, "radius_pm": 186.0, "ionization_ev": 5.1391},
            {"symbol": "K", "period": 4, "mass_u": 39.0983, "radius_pm": 227.0, "ionization_ev": 4.3407},
            {"symbol": "Rb", "period": 5, "mass_u": 85.4678, "radius_pm": 248.0, "ionization_ev": 4.1771},
            {"symbol": "Cs", "period": 6, "mass_u": 132.90545196, "radius_pm": 267.0, "ionization_ev": 3.8939},
        ],
    },
    "halogen": {
        "l_valence": 1,
        "l_core": 0,
        "items": [
            {"symbol": "F", "period": 2, "mass_u": 18.998403163, "radius_pm": 50.0, "ionization_ev": 17.4228},
            {"symbol": "Cl", "period": 3, "mass_u": 35.45, "radius_pm": 79.0, "ionization_ev": 12.9676},
            {"symbol": "Br", "period": 4, "mass_u": 79.904, "radius_pm": 94.0, "ionization_ev": 11.8138},
            {"symbol": "I", "period": 5, "mass_u": 126.90447, "radius_pm": 115.0, "ionization_ev": 10.4513},
        ],
    },
    "transition_3d": {
        "l_valence": 2,
        "l_core": 1,
        "items": [
            {"symbol": "Sc", "period": 4, "mass_u": 44.955908, "radius_pm": 162.0, "ionization_ev": 6.5615},
            {"symbol": "Ti", "period": 4, "mass_u": 47.867, "radius_pm": 147.0, "ionization_ev": 6.8281},
            {"symbol": "V", "period": 4, "mass_u": 50.9415, "radius_pm": 134.0, "ionization_ev": 6.7462},
            {"symbol": "Cr", "period": 4, "mass_u": 51.9961, "radius_pm": 128.0, "ionization_ev": 6.7665},
            {"symbol": "Mn", "period": 4, "mass_u": 54.938044, "radius_pm": 127.0, "ionization_ev": 7.4340},
            {"symbol": "Fe", "period": 4, "mass_u": 55.845, "radius_pm": 126.0, "ionization_ev": 7.9024},
            {"symbol": "Co", "period": 4, "mass_u": 58.933194, "radius_pm": 125.0, "ionization_ev": 7.8810},
            {"symbol": "Ni", "period": 4, "mass_u": 58.6934, "radius_pm": 124.0, "ionization_ev": 7.6398},
            {"symbol": "Cu", "period": 4, "mass_u": 63.546, "radius_pm": 128.0, "ionization_ev": 7.7264},
            {"symbol": "Zn", "period": 4, "mass_u": 65.38, "radius_pm": 134.0, "ionization_ev": 9.3942},
        ],
    },
    "transition_4d": {
        "l_valence": 2,
        "l_core": 1,
        "items": [
            {"symbol": "Y", "period": 5, "mass_u": 88.90584, "radius_pm": 180.0, "ionization_ev": 6.2173},
            {"symbol": "Zr", "period": 5, "mass_u": 91.224, "radius_pm": 155.0, "ionization_ev": 6.6339},
            {"symbol": "Nb", "period": 5, "mass_u": 92.90637, "radius_pm": 146.0, "ionization_ev": 6.7589},
            {"symbol": "Mo", "period": 5, "mass_u": 95.95, "radius_pm": 139.0, "ionization_ev": 7.0924},
            {"symbol": "Tc", "period": 5, "mass_u": 98.0, "radius_pm": 136.0, "ionization_ev": 7.2800},
            {"symbol": "Ru", "period": 5, "mass_u": 101.07, "radius_pm": 134.0, "ionization_ev": 7.3605},
            {"symbol": "Rh", "period": 5, "mass_u": 102.9055, "radius_pm": 134.0, "ionization_ev": 7.4589},
            {"symbol": "Pd", "period": 5, "mass_u": 106.42, "radius_pm": 137.0, "ionization_ev": 8.3369},
            {"symbol": "Ag", "period": 5, "mass_u": 107.8682, "radius_pm": 144.0, "ionization_ev": 7.5762},
            {"symbol": "Cd", "period": 5, "mass_u": 112.414, "radius_pm": 151.0, "ionization_ev": 8.9938},
        ],
    },
    "transition_5d": {
        "l_valence": 2,
        "l_core": 1,
        "items": [
            {"symbol": "Hf", "period": 6, "mass_u": 178.49, "radius_pm": 159.0, "ionization_ev": 6.8251},
            {"symbol": "Ta", "period": 6, "mass_u": 180.94788, "radius_pm": 146.0, "ionization_ev": 7.5496},
            {"symbol": "W", "period": 6, "mass_u": 183.84, "radius_pm": 139.0, "ionization_ev": 7.8640},
            {"symbol": "Re", "period": 6, "mass_u": 186.207, "radius_pm": 137.0, "ionization_ev": 7.8335},
            {"symbol": "Os", "period": 6, "mass_u": 190.23, "radius_pm": 135.0, "ionization_ev": 8.4382},
            {"symbol": "Ir", "period": 6, "mass_u": 192.217, "radius_pm": 136.0, "ionization_ev": 8.9670},
            {"symbol": "Pt", "period": 6, "mass_u": 195.084, "radius_pm": 139.0, "ionization_ev": 8.9588},
            {"symbol": "Au", "period": 6, "mass_u": 196.96657, "radius_pm": 144.0, "ionization_ev": 9.2255},
            {"symbol": "Hg", "period": 6, "mass_u": 200.592, "radius_pm": 151.0, "ionization_ev": 10.4375},
        ],
    },
    "lanthanide": {
        "l_valence": 3,
        "l_core": 2,
        "items": [
            {"symbol": "La", "period": 6, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.5770},
            {"symbol": "Ce", "period": 6, "mass_u": 140.11600, "radius_pm": 185.0, "ionization_ev": 5.5387},
            {"symbol": "Pr", "period": 6, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.4730},
            {"symbol": "Nd", "period": 6, "mass_u": 144.24200, "radius_pm": 181.0, "ionization_ev": 5.5250},
            {"symbol": "Sm", "period": 6, "mass_u": 150.36000, "radius_pm": 180.0, "ionization_ev": 5.6440},
            {"symbol": "Eu", "period": 6, "mass_u": 151.96400, "radius_pm": 199.0, "ionization_ev": 5.6700},
            {"symbol": "Gd", "period": 6, "mass_u": 157.25000, "radius_pm": 180.0, "ionization_ev": 6.1500},
            {"symbol": "Tb", "period": 6, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.8630},
            {"symbol": "Dy", "period": 6, "mass_u": 162.50000, "radius_pm": 177.0, "ionization_ev": 5.9390},
            {"symbol": "Ho", "period": 6, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.0220},
            {"symbol": "Er", "period": 6, "mass_u": 167.25900, "radius_pm": 175.0, "ionization_ev": 6.1080},
            {"symbol": "Tm", "period": 6, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.1840},
            {"symbol": "Yb", "period": 6, "mass_u": 173.04500, "radius_pm": 194.0, "ionization_ev": 6.2540},
            {"symbol": "Lu", "period": 6, "mass_u": 174.96680, "radius_pm": 173.0, "ionization_ev": 5.4280},
        ],
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            raise ValueError("singular system")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot = augmented[pivot_index][pivot_index]
        for column_index in range(pivot_index, size + 1):
            augmented[pivot_index][column_index] /= pivot

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column_index in range(pivot_index, size + 1):
                augmented[row_index][column_index] -= factor * augmented[pivot_index][column_index]

    return [augmented[row_index][size] for row_index in range(size)]


def fit_multivariate(rows: list[list[float]], targets: list[float]) -> dict:
    columns = len(rows[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]

    for row, target in zip(rows, targets):
        for i in range(columns):
            xty[i] += row[i] * target
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]

    coefficients = solve_linear_system(xtx, xty)
    predicted = [sum(coefficient * value for coefficient, value in zip(coefficients, row)) for row in rows]
    residuals = [target - prediction for target, prediction in zip(targets, predicted)]
    rmse = math.sqrt(sum(residual * residual for residual in residuals) / len(residuals))
    return {
        "coefficients": coefficients,
        "predicted": predicted,
        "residuals": residuals,
        "rmse": rmse,
        "max_abs_residual": max(abs(residual) for residual in residuals),
    }


def build_observables() -> dict:
    items = []
    radii = []
    zeff_values = []
    valence_values = []
    core_values = []
    ratio_values = []

    for family_name, family in FAMILIES.items():
        l_valence = float(family["l_valence"])
        l_core = float(family["l_core"])
        ratio = (l_valence + 0.5) / (l_core + 0.5)
        for item in family["items"]:
            zeff = estimate_zeff(item["ionization_ev"], int(item["period"]))
            entry = {
                **item,
                "family": family_name,
                "l_valence": l_valence,
                "l_core": l_core,
                "core_valence_ratio": round(ratio, 6),
                "zeff_proxy": round(zeff, 6),
            }
            items.append(entry)
            radii.append(item["radius_pm"])
            zeff_values.append(zeff)
            valence_values.append(l_valence)
            core_values.append(l_core)
            ratio_values.append(ratio)

    return {
        "series": items,
        "radii": radii,
        "zeff_values": zeff_values,
        "valence_values": valence_values,
        "core_values": core_values,
        "ratio_values": ratio_values,
    }


def fit_baseline(observables: dict) -> dict:
    rows = [[1.0, zeff] for zeff in observables["zeff_values"]]
    fit = fit_multivariate(rows, observables["radii"])
    return {
        "fit": {
            "intercept": fit["coefficients"][0],
            "alpha": fit["coefficients"][1],
        },
        **fit,
    }


def fit_corrected(observables: dict) -> dict:
    rows = [[1.0, zeff, l_valence, l_core] for zeff, l_valence, l_core in zip(observables["zeff_values"], observables["valence_values"], observables["core_values"])]
    fit = fit_multivariate(rows, observables["radii"])
    return {
        "fit": {
            "intercept": fit["coefficients"][0],
            "alpha": fit["coefficients"][1],
            "beta": fit["coefficients"][2],
            "gamma": fit["coefficients"][3],
        },
        **fit,
    }


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    observables = build_observables()
    baseline = fit_baseline(observables)
    corrected = fit_corrected(observables)

    corrected_better = corrected["rmse"] < baseline["rmse"] and corrected["max_abs_residual"] <= baseline["max_abs_residual"]
    monotone_radius = trend(observables["radii"]) == "increasing"
    monotone_zeff = trend(observables["zeff_values"]) == "increasing"
    ratio_spread = statistics.pstdev(observables["ratio_values"])

    verdict = "supported" if corrected_better and monotone_radius and monotone_zeff else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "corrected_better": corrected_better,
        "monotone_radius": monotone_radius,
        "monotone_zeff": monotone_zeff,
        "ratio_spread": ratio_spread,
        "baseline": baseline,
        "corrected": corrected,
        "hypothesis": "an explicit core/valence correction reduces radius residuals across representative families",
        "case_control": "baseline radius fit against Z_eff versus corrected fit against [1, Z_eff, l_valence, l_core]",
        "observable": "radius residuals across representative s, p, d and f families",
        "family": observables["series"],
    }

    json_path = outdir / f"core_valence_correction_check_{timestamp}.json"
    txt_path = outdir / f"core_valence_correction_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Core / valence correction check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Verdict: {verdict}\n\n")
        handle.write("Famille:\n")
        for item in observables["series"]:
            handle.write(
                f"- {item['symbol']} ({item['family']}): radius={item['radius_pm']:.1f} pm, ie={item['ionization_ev']:.4f} eV, "
                f"zeff={item['zeff_proxy']}, l_valence={item['l_valence']}, l_core={item['l_core']}, ratio={item['core_valence_ratio']}\n"
            )
        handle.write("\nBaseline:\n")
        handle.write(f"- intercept: {baseline['fit']['intercept']:.6f}\n")
        handle.write(f"- alpha: {baseline['fit']['alpha']:.6f}\n")
        handle.write(f"- rmse: {baseline['rmse']:.6f}\n")
        handle.write(f"- max_abs_residual: {baseline['max_abs_residual']:.6f}\n")
        handle.write("\nCorrected:\n")
        handle.write(f"- intercept: {corrected['fit']['intercept']:.6f}\n")
        handle.write(f"- alpha: {corrected['fit']['alpha']:.6f}\n")
        handle.write(f"- beta: {corrected['fit']['beta']:.6f}\n")
        handle.write(f"- gamma: {corrected['fit']['gamma']:.6f}\n")
        handle.write(f"- rmse: {corrected['rmse']:.6f}\n")
        handle.write(f"- max_abs_residual: {corrected['max_abs_residual']:.6f}\n")
        handle.write(f"- corrected_better: {corrected_better}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {verdict}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    run_check(args.output_dir)


if __name__ == "__main__":
    main()