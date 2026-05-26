"""Fine tetrel subseries check using Zeff* as the main structural variable.

This replays the C -> Ge / Ge -> Pb split, but replaces the Bohr-style Zeff
proxy with the corrected Zeff* used in the rest of the D1_atom setup.

For each subseries, the script compares:
- radius ~ mass
- radius ~ raw Zeff
- radius ~ Zeff*
- radius ~ [1, Zeff*, k, L]

The goal is to see whether Zeff* becomes the best organizer in both subseries
and whether the shared pivot Ge stays consistent across the two fits.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
A_K = 0.0
B_L = 0.25
C_Z2 = 1.1e-4
D_H = 0.0

FAMILY = [
    {"symbol": "C", "Z": 6, "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603, "k": 0.0, "L": 0.0, "H": 0.0},
    {"symbol": "Si", "Z": 14, "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517, "k": 0.0, "L": 1.0, "H": 0.0},
    {"symbol": "Ge", "Z": 32, "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994, "k": 0.0, "L": 2.0, "H": 0.0},
    {"symbol": "Sn", "Z": 50, "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439, "k": 0.0, "L": 3.0, "H": 0.0},
    {"symbol": "Pb", "Z": 82, "period": 6, "mass_u": 207.200, "radius_pm": 154.0, "ionization_ev": 7.4167, "k": 0.0, "L": 3.0, "H": 0.0},
]

LIGHT_CORE = FAMILY[:3]
HEAVY_TAIL = FAMILY[2:]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def estimate_zeff_star(item: dict) -> float:
    zeff = estimate_zeff(item["ionization_ev"], item["period"])
    return zeff + (A_K * item["k"]) + (B_L * item["L"]) + (C_Z2 * (item["Z"] ** 2)) + (D_H * item["H"])


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
    zeff_star_values = []
    masses = []
    radii = []
    ionizations = []
    ks = []
    ls = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        zeff_star = estimate_zeff_star(item)
        evaluated.append({**item, "zeff_proxy": round(zeff, 6), "zeff_star": round(zeff_star, 6)})
        zeff_values.append(zeff)
        zeff_star_values.append(zeff_star)
        masses.append(item["mass_u"])
        radii.append(item["radius_pm"])
        ionizations.append(item["ionization_ev"])
        ks.append(item["k"])
        ls.append(item["L"])

    mass_slope, mass_intercept = linear_fit(masses, radii)
    zeff_slope, zeff_intercept = linear_fit(zeff_values, radii)
    zeff_star_slope, zeff_star_intercept = linear_fit(zeff_star_values, radii)

    mass_predicted = [mass_slope * value + mass_intercept for value in masses]
    zeff_predicted = [zeff_slope * value + zeff_intercept for value in zeff_values]
    zeff_star_predicted = [zeff_star_slope * value + zeff_star_intercept for value in zeff_star_values]

    corrected_rows = [[1.0, zeff_star, k, l] for zeff_star, k, l in zip(zeff_star_values, ks, ls)]
    corrected_fit = fit_multivariate(corrected_rows, radii)

    return {
        "series": evaluated,
        "radius_trend": trend(radii),
        "ionization_trend": trend(ionizations),
        "zeff_trend": trend(zeff_values),
        "zeff_star_trend": trend(zeff_star_values),
        "mass_trend": trend(masses),
        "mass": {
            "fit": {"slope": mass_slope, "intercept": mass_intercept},
            "predicted": mass_predicted,
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, mass_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, mass_predicted)),
        },
        "zeff": {
            "fit": {"slope": zeff_slope, "intercept": zeff_intercept},
            "predicted": zeff_predicted,
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, zeff_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, zeff_predicted)),
        },
        "zeff_star": {
            "fit": {"slope": zeff_star_slope, "intercept": zeff_star_intercept},
            "predicted": zeff_star_predicted,
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, zeff_star_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, zeff_star_predicted)),
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
    zeff_star_better_light = light_metrics["zeff_star"]["rmse"] <= light_metrics["zeff"]["rmse"] and light_metrics["zeff_star"]["rmse"] <= light_metrics["mass"]["rmse"]
    zeff_star_better_heavy = heavy_metrics["zeff_star"]["rmse"] <= heavy_metrics["zeff"]["rmse"] and heavy_metrics["zeff_star"]["rmse"] <= heavy_metrics["mass"]["rmse"]
    corrected_better_light = light_metrics["corrected"]["rmse"] <= light_metrics["zeff_star"]["rmse"]
    corrected_better_heavy = heavy_metrics["corrected"]["rmse"] <= heavy_metrics["zeff_star"]["rmse"]
    radius_ok = (
        light_metrics["radius_trend"] == "increasing"
        and heavy_metrics["radius_trend"] == "increasing"
        and light_metrics["zeff_star_trend"] == "increasing"
        and heavy_metrics["zeff_star_trend"] == "increasing"
        and zeff_star_better_light
        and zeff_star_better_heavy
        and corrected_better_light
        and corrected_better_heavy
    )
    ionization_ok = (
        light_metrics["radius_trend"] == "increasing"
        and light_metrics["ionization_trend"] == "decreasing"
        and heavy_metrics["radius_trend"] == "increasing"
        and heavy_metrics["ionization_trend"] == "mixed"
    )

    if radius_ok:
        verdict = "supported"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "using Zeff* as the fine subseries variable keeps both tetrel subseries regular and improves over mass and raw Zeff",
        "case_control": "C -> Si -> Ge versus Ge -> Sn -> Pb, with radius compared against mass, raw Zeff, Zeff*, and [1, Zeff*, k, L]",
        "observable": "subseries fit quality, monotonicity, and pivot consistency at Ge",
        "expected": {
            "light_core": "Zeff* beats mass and raw Zeff, corrected fit does not worsen it",
            "heavy_tail": "Zeff* beats mass and raw Zeff, corrected fit does not worsen it",
        },
        "measured": {
            "light_core": light_metrics,
            "heavy_tail": heavy_metrics,
        },
        "criteria": {
            "zeff_star_better_light": zeff_star_better_light,
            "zeff_star_better_heavy": zeff_star_better_heavy,
            "corrected_better_light": corrected_better_light,
            "corrected_better_heavy": corrected_better_heavy,
            "radius_ok": radius_ok,
            "ionization_ok": ionization_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "one of the subseries is not monotone in radius or Zeff*",
            "Zeff* does not improve on both mass and raw Zeff in the light core",
            "Zeff* does not improve on both mass and raw Zeff in the heavy tail",
            "the corrected fit [1, Zeff*, k, L] does not match or improve the Zeff* baseline",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fine tetrel subseries using Zeff* as the structural variable.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    light_metrics = analyze_series(LIGHT_CORE)
    heavy_metrics = analyze_series(HEAVY_TAIL)
    results = classify(light_metrics, heavy_metrics)

    json_path = outdir / f"tetrel_subseries_zeff_star_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_subseries_zeff_star_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel subseries Zeff* check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Sous-serie legere C -> Ge:\n")
        handle.write(f"- mass_rmse: {light_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {light_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {light_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {light_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_trend: {light_metrics['zeff_star_trend']}\n")
        handle.write(f"- ionization_trend: {light_metrics['ionization_trend']}\n")
        handle.write("\nSous-serie lourde Ge -> Pb:\n")
        handle.write(f"- mass_rmse: {heavy_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {heavy_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {heavy_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {heavy_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_trend: {heavy_metrics['zeff_star_trend']}\n")
        handle.write(f"- ionization_trend: {heavy_metrics['ionization_trend']}\n")
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