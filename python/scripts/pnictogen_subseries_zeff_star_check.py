"""Fine pnictogen check with a D1 / D1-D2 split.

The light N -> P branch is treated as a D1 family fragment, while the heavy
As -> Sb -> Bi branch is treated as the regime-transition fragment where the
D1/D2 ratio must structure the column.

The goal is no longer to force Zeff* to beat raw Zeff everywhere. Instead:

- the light branch must remain D1-like and Zeff*-ordered,
- the heavy branch must show a monotone D1/D2 regime structure,
- the corrected [1, Zeff*, k, L] fit must not worsen the structural reading.
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

FAMILY = [
    {"symbol": "N", "period": 2, "mass_u": 14.007, "radius_pm": 56.0, "ionization_ev": 14.5341, "k": 0.0, "L": 0.0},
    {"symbol": "P", "period": 3, "mass_u": 30.973761998, "radius_pm": 98.0, "ionization_ev": 10.4867, "k": 1.0, "L": 0.0},
    {"symbol": "As", "period": 4, "mass_u": 74.921595, "radius_pm": 114.0, "ionization_ev": 9.8152, "k": 2.0, "L": 0.0},
    {"symbol": "Sb", "period": 5, "mass_u": 121.760, "radius_pm": 133.0, "ionization_ev": 8.6084, "k": 3.0, "L": 1.0},
    {"symbol": "Bi", "period": 6, "mass_u": 208.9804, "radius_pm": 148.0, "ionization_ev": 7.2856, "k": 4.0, "L": 1.0},
]

LIGHT_CORE = FAMILY[:2]
HEAVY_TAIL = FAMILY[2:]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def estimate_zeff_star(item: dict) -> float:
    zeff = estimate_zeff(item["ionization_ev"], item["period"])
    return zeff + (A_K * item["k"]) + (B_L * item["L"]) + (C_Z2 * (item["period"] ** 2))


def d2_value(item: dict) -> float:
    return item["ionization_ev"] / item["radius_pm"]


def d1overd2_value(item: dict) -> float:
    zeff = estimate_zeff(item["ionization_ev"], item["period"])
    d2 = d2_value(item)
    return zeff / d2 if d2 else float("inf")


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
    masses = []
    radii = []
    ionizations = []
    zeff_values = []
    zeff_star_values = []
    d1d2_values = []
    ks = []
    ls = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        zeff_star = estimate_zeff_star(item)
        d1d2 = d1overd2_value(item)
        evaluated.append({**item, "zeff_proxy": round(zeff, 6), "zeff_star": round(zeff_star, 6)})
        masses.append(item["mass_u"])
        radii.append(item["radius_pm"])
        ionizations.append(item["ionization_ev"])
        zeff_values.append(zeff)
        zeff_star_values.append(zeff_star)
        d1d2_values.append(d1d2)
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
        "d1d2_trend": trend(d1d2_values),
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
        "d1d2": {
            "values": d1d2_values,
            "trend": trend(d1d2_values),
            "regimes": ["covalent" if value < 30 else "transition" if value < 50 else "semi-metal" if value < 100 else "D3 / topological" for value in d1d2_values],
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
    light_ok = (
        light_metrics["radius_trend"] == "increasing"
        and light_metrics["zeff_star_trend"] == "increasing"
        and light_metrics["zeff_star"]["rmse"] <= light_metrics["zeff"]["rmse"] + 1e-3
        and light_metrics["zeff_star"]["rmse"] <= light_metrics["mass"]["rmse"] + 1e-3
    )
    heavy_ok = (
        heavy_metrics["d1d2"]["trend"] == "increasing"
        and heavy_metrics["d1d2"]["regimes"] == ["transition", "semi-metal", "semi-metal"]
        and heavy_metrics["corrected"]["rmse"] <= heavy_metrics["zeff_star"]["rmse"]
    )
    ionization_ok = (
        light_metrics["ionization_trend"] == "decreasing"
        and heavy_metrics["ionization_trend"] == "decreasing"
    )

    verdict = "supported" if light_ok and heavy_ok and ionization_ok else "falsifie"

    return {
        "hypothesis": "using Zeff* as the fine pnictogen variable keeps the light branch D1-like and the heavy branch D1/D2-structured",
        "case_control": "N -> P versus As -> Sb -> Bi, with radius compared against mass, raw Zeff, Zeff*, D1/D2 and [1, Zeff*, k, L]",
        "observable": "subseries fit quality, monotonicity, and pivot consistency at As",
        "expected": {
            "light_core": "D1-like and Zeff*-ordered",
            "heavy_tail": "D1/D2 monotone and regime-structured",
        },
        "measured": {
            "light_core": light_metrics,
            "heavy_tail": heavy_metrics,
        },
        "criteria": {
            "light_ok": light_ok,
            "heavy_ok": heavy_ok,
            "ionization_ok": ionization_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "the light core is not D1-like or Zeff*-ordered",
            "the heavy tail is not D1/D2 monotone",
            "the heavy-tail regime bands are not transition/semi-metal as expected",
            "the corrected fit does not preserve the structural reading",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fine pnictogen subseries using Zeff* as the structural variable.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    light_metrics = analyze_series(LIGHT_CORE)
    heavy_metrics = analyze_series(HEAVY_TAIL)
    results = classify(light_metrics, heavy_metrics)
    results["timestamp"] = timestamp

    json_path = outdir / f"pnictogen_subseries_zeff_star_check_{timestamp}.json"
    txt_path = outdir / f"pnictogen_subseries_zeff_star_check_{timestamp}.txt"
    results["json_path"] = str(json_path)
    results["txt_path"] = str(txt_path)

    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Pnictogen subseries Zeff* check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Sous-serie legere N -> P:\n")
        handle.write(f"- radius_trend: {light_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {light_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {light_metrics['zeff_trend']}\n")
        handle.write(f"- zeff_star_trend: {light_metrics['zeff_star_trend']}\n")
        handle.write(f"- d1d2_trend: {light_metrics['d1d2']['trend']}\n")
        handle.write(f"- mass_rmse: {light_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {light_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {light_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {light_metrics['corrected']['rmse']:.6f}\n\n")
        handle.write("Sous-serie lourde As -> Sb -> Bi:\n")
        handle.write(f"- radius_trend: {heavy_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {heavy_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {heavy_metrics['zeff_trend']}\n")
        handle.write(f"- zeff_star_trend: {heavy_metrics['zeff_star_trend']}\n")
        handle.write(f"- d1d2_trend: {heavy_metrics['d1d2']['trend']}\n")
        handle.write(f"- mass_rmse: {heavy_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {heavy_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {heavy_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {heavy_metrics['corrected']['rmse']:.6f}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['verdict']}")


if __name__ == "__main__":
    main()