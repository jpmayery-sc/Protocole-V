"""Test the candidate k/L correction on the fine tetrel subseries.

The earlier fine-split test showed that mass does not return as a useful
organizer once the tetrel family is cut at Ge. This script reuses the same
subseries split but checks whether the structural correction

    radius ~ intercept + alpha * Z_eff + beta * k + gamma * L

improves the residuals in both subseries.
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
    {"symbol": "C", "name": "Carbon", "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603, "k": 0.0, "L": 0.0},
    {"symbol": "Si", "name": "Silicon", "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517, "k": 0.0, "L": 1.0},
    {"symbol": "Ge", "name": "Germanium", "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994, "k": 0.0, "L": 2.0},
    {"symbol": "Sn", "name": "Tin", "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439, "k": 0.0, "L": 3.0},
    {"symbol": "Pb", "name": "Lead", "period": 6, "mass_u": 207.200, "radius_pm": 154.0, "ionization_ev": 7.4167, "k": 0.0, "L": 3.0},
]

LIGHT_CORE = FAMILY[:3]
HEAVY_TAIL = FAMILY[2:]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


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


def fit_multivariate(rows: list[list[float]], targets: list[float], ridge: float = 1e-6) -> dict:
    columns = len(rows[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]

    for row, target in zip(rows, targets):
        for i in range(columns):
            xty[i] += row[i] * target
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]

    for diagonal in range(columns):
        xtx[diagonal][diagonal] += ridge

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


def analyze_series(series: list[dict]) -> dict:
    evaluated = []
    zeff_values = []
    radii = []
    masses = []
    ks = []
    ls = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        evaluated.append({**item, "zeff_proxy": round(zeff, 6)})
        zeff_values.append(zeff)
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        ks.append(item["k"])
        ls.append(item["L"])

    baseline_slope, baseline_intercept = linear_fit(zeff_values, radii)
    baseline_predicted = [baseline_slope * value + baseline_intercept for value in zeff_values]
    baseline_residuals = [radius - prediction for radius, prediction in zip(radii, baseline_predicted)]

    corrected_rows = [[1.0, zeff, k, l] for zeff, k, l in zip(zeff_values, ks, ls)]
    corrected_fit = fit_multivariate(corrected_rows, radii)

    return {
        "series": evaluated,
        "radius_trend": trend(radii),
        "ionization_trend": trend([item["ionization_ev"] for item in series]),
        "zeff_trend": trend(zeff_values),
        "mass_trend": trend(masses),
        "baseline": {
            "fit": {"slope": baseline_slope, "intercept": baseline_intercept},
            "predicted": baseline_predicted,
            "residuals": baseline_residuals,
            "rmse": math.sqrt(sum(residual * residual for residual in baseline_residuals) / len(baseline_residuals)),
            "max_abs_residual": max(abs(residual) for residual in baseline_residuals),
        },
        "corrected": {
            "fit": {
                "intercept": corrected_fit["coefficients"][0],
                "alpha": corrected_fit["coefficients"][1],
                "beta": corrected_fit["coefficients"][2],
                "gamma": corrected_fit["coefficients"][3],
            },
            **corrected_fit,
        },
    }


def classify(light_metrics: dict, heavy_metrics: dict) -> dict:
    light_corrected_better = light_metrics["corrected"]["rmse"] < light_metrics["baseline"]["rmse"]
    heavy_corrected_better = heavy_metrics["corrected"]["rmse"] < heavy_metrics["baseline"]["rmse"]
    structural_ok = (
        light_metrics["radius_trend"] == "increasing"
        and heavy_metrics["radius_trend"] == "increasing"
    )

    if structural_ok and light_corrected_better and heavy_corrected_better:
        verdict = "supported"
    elif structural_ok and (light_corrected_better or heavy_corrected_better):
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "the fine tetrel subseries becomes more regular when the k/L correction is used instead of the mass-return reading",
        "case_control": "C -> Si -> Ge versus Ge -> Sn -> Pb, baseline Z_eff fit versus corrected [1, Z_eff, k, L] fit",
        "observable": "radius residuals and fit regularity in the two tetrel subseries",
        "expected": {
            "light_core": "corrected fit smoother than baseline",
            "heavy_tail": "corrected fit smoother than baseline",
            "ionization": "may remain mixed on the heavy tail",
        },
        "measured": {
            "light_core": light_metrics,
            "heavy_tail": heavy_metrics,
        },
        "criteria": {
            "light_corrected_better": light_corrected_better,
            "heavy_corrected_better": heavy_corrected_better,
            "structural_ok": structural_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "one of the subseries is not monotone in radius and ionization",
            "the corrected fit does not improve the light core",
            "the corrected fit does not improve the heavy tail",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fine tetrel subseries with the k/L correction.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    light_metrics = analyze_series(LIGHT_CORE)
    heavy_metrics = analyze_series(HEAVY_TAIL)
    results = classify(light_metrics, heavy_metrics)

    json_path = outdir / f"tetrel_subseries_k_l_correction_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_subseries_k_l_correction_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel subseries k/L correction check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Sous-serie legere C -> Ge:\n")
        handle.write(f"- baseline_rmse: {light_metrics['baseline']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {light_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- baseline_max_abs_residual: {light_metrics['baseline']['max_abs_residual']:.6f}\n")
        handle.write(f"- corrected_max_abs_residual: {light_metrics['corrected']['max_abs_residual']:.6f}\n")
        handle.write("\nSous-serie lourde Ge -> Pb:\n")
        handle.write(f"- baseline_rmse: {heavy_metrics['baseline']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {heavy_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- baseline_max_abs_residual: {heavy_metrics['baseline']['max_abs_residual']:.6f}\n")
        handle.write(f"- corrected_max_abs_residual: {heavy_metrics['corrected']['max_abs_residual']:.6f}\n")
        handle.write("\nCriteres:\n")
        for key, value in results["criteria"].items():
            handle.write(f"- {key}: {value}\n")
        handle.write("\nFalsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['verdict']}")


if __name__ == "__main__":
    main()