"""Test the candidate k/L correction on the lanthanide family.

The check compares a baseline radius fit against Z_eff with an augmented fit
that adds the local variables k and L directly:

    radius ~ intercept + alpha * Z_eff + beta * k + gamma * L

The goal is to see whether the correction reduces the f-block residuals while
keeping the full La -> Lu series in view.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
FAMILY = [
    {"symbol": "La", "period": 6, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.5770, "k": 0.0, "L": 0.0},
    {"symbol": "Ce", "period": 6, "mass_u": 140.11600, "radius_pm": 185.0, "ionization_ev": 5.5387, "k": 1.0, "L": 0.0},
    {"symbol": "Pr", "period": 6, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.4730, "k": 2.0, "L": 0.0},
    {"symbol": "Nd", "period": 6, "mass_u": 144.24200, "radius_pm": 181.0, "ionization_ev": 5.5250, "k": 3.0, "L": 0.0},
    {"symbol": "Sm", "period": 6, "mass_u": 150.36000, "radius_pm": 180.0, "ionization_ev": 5.6440, "k": 4.0, "L": 0.0},
    {"symbol": "Eu", "period": 6, "mass_u": 151.96400, "radius_pm": 199.0, "ionization_ev": 5.6700, "k": 5.0, "L": 1.0},
    {"symbol": "Gd", "period": 6, "mass_u": 157.25000, "radius_pm": 180.0, "ionization_ev": 6.1500, "k": 6.0, "L": 0.0},
    {"symbol": "Tb", "period": 6, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.8630, "k": 7.0, "L": 0.0},
    {"symbol": "Dy", "period": 6, "mass_u": 162.50000, "radius_pm": 177.0, "ionization_ev": 5.9390, "k": 8.0, "L": 0.0},
    {"symbol": "Ho", "period": 6, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.0220, "k": 9.0, "L": 0.0},
    {"symbol": "Er", "period": 6, "mass_u": 167.25900, "radius_pm": 175.0, "ionization_ev": 6.1080, "k": 10.0, "L": 0.0},
    {"symbol": "Tm", "period": 6, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.1840, "k": 11.0, "L": 0.0},
    {"symbol": "Yb", "period": 6, "mass_u": 173.04500, "radius_pm": 194.0, "ionization_ev": 6.2540, "k": 12.0, "L": 1.0},
    {"symbol": "Lu", "period": 6, "mass_u": 174.96680, "radius_pm": 173.0, "ionization_ev": 5.4280, "k": 13.0, "L": 0.0},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


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


def build_observables(series: list[dict]) -> dict:
    items = []
    zeff_values = []
    radii = []
    masses = []
    ks = []
    ls = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        items.append({**item, "zeff_proxy": round(zeff, 6)})
        zeff_values.append(zeff)
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        ks.append(item["k"])
        ls.append(item["L"])

    return {
        "series": items,
        "zeff_values": zeff_values,
        "radii": radii,
        "masses": masses,
        "ks": ks,
        "ls": ls,
    }


def fit_baseline(observables: dict) -> dict:
    slope, intercept = linear_fit(observables["zeff_values"], observables["radii"])
    predicted = [slope * value + intercept for value in observables["zeff_values"]]
    residuals = [radius - prediction for radius, prediction in zip(observables["radii"], predicted)]
    return {
        "fit": {"slope": slope, "intercept": intercept},
        "predicted": predicted,
        "residuals": residuals,
        "rmse": math.sqrt(sum(residual * residual for residual in residuals) / len(residuals)),
        "max_abs_residual": max(abs(residual) for residual in residuals),
    }


def fit_corrected(observables: dict) -> dict:
    rows = [[1.0, zeff, k, l] for zeff, k, l in zip(observables["zeff_values"], observables["ks"], observables["ls"])]
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
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    observables = build_observables(FAMILY)
    baseline = fit_baseline(observables)
    corrected = fit_corrected(observables)

    corrected_better = corrected["rmse"] < baseline["rmse"] and corrected["max_abs_residual"] <= baseline["max_abs_residual"]
    monotone_radius = trend(observables["radii"]) == "mixed"
    monotone_zeff = trend(observables["zeff_values"]) == "mixed"

    verdict = "supported" if corrected_better else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "corrected_better": corrected_better,
        "monotone_radius": monotone_radius,
        "monotone_zeff": monotone_zeff,
        "baseline": baseline,
        "corrected": corrected,
        "hypothesis": "for the lanthanide family, adding local k and L terms to Z_eff reduces radius residuals",
        "case_control": "baseline radius fit against Z_eff versus corrected fit against [1, Z_eff, k, L]",
        "observable": "radius residuals on the lanthanide family",
        "family": observables["series"],
    }

    json_path = outdir / f"lanthanide_k_l_correction_check_{timestamp}.json"
    txt_path = outdir / f"lanthanide_k_l_correction_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Lanthanide k/L correction check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Verdict: {verdict}\n\n")
        handle.write("Famille:\n")
        for item in observables["series"]:
            handle.write(
                f"- {item['symbol']}: radius={item['radius_pm']:.1f} pm, ie={item['ionization_ev']:.4f} eV, "
                f"zeff={item['zeff_proxy']}, k={item['k']}, L={item['L']}\n"
            )
        handle.write("\nBaseline:\n")
        handle.write(f"- slope: {baseline['fit']['slope']:.6f}\n")
        handle.write(f"- intercept: {baseline['fit']['intercept']:.6f}\n")
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