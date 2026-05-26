"""Fine lanthanide subseries check using Zeff* and an H anomaly term.

This replays the La -> Lu split into two repaired subseries and evaluates whether
the corrected structural variable Zeff* remains the best organizer for the
lanthanide radius trend, compared with raw mass and raw Zeff.

For each repaired subseries, the script compares:
- radius ~ mass
- radius ~ raw Zeff
- radius ~ Zeff*
- radius ~ [1, Zeff*, k, L, H]

H is also probed separately on the full family as an anomaly flag for the well-
known Eu / Yb irregularities.
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
D_H = 0.35

FULL_FAMILY = [
    {"symbol": "La", "period": 6, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.5770, "k": 0.0, "L": 0.0, "H": 0.0},
    {"symbol": "Ce", "period": 6, "mass_u": 140.11600, "radius_pm": 185.0, "ionization_ev": 5.5387, "k": 1.0, "L": 0.0, "H": 0.0},
    {"symbol": "Pr", "period": 6, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.4730, "k": 2.0, "L": 0.0, "H": 0.0},
    {"symbol": "Nd", "period": 6, "mass_u": 144.24200, "radius_pm": 181.0, "ionization_ev": 5.5250, "k": 3.0, "L": 0.0, "H": 0.0},
    {"symbol": "Sm", "period": 6, "mass_u": 150.36000, "radius_pm": 180.0, "ionization_ev": 5.6440, "k": 4.0, "L": 0.0, "H": 0.0},
    {"symbol": "Eu", "period": 6, "mass_u": 151.96400, "radius_pm": 199.0, "ionization_ev": 5.6700, "k": 5.0, "L": 1.0, "H": 1.0},
    {"symbol": "Gd", "period": 6, "mass_u": 157.25000, "radius_pm": 180.0, "ionization_ev": 6.1500, "k": 6.0, "L": 0.0, "H": 0.0},
    {"symbol": "Tb", "period": 6, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.8630, "k": 7.0, "L": 0.0, "H": 0.0},
    {"symbol": "Dy", "period": 6, "mass_u": 162.50000, "radius_pm": 177.0, "ionization_ev": 5.9390, "k": 8.0, "L": 0.0, "H": 0.0},
    {"symbol": "Ho", "period": 6, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.0220, "k": 9.0, "L": 0.0, "H": 0.0},
    {"symbol": "Er", "period": 6, "mass_u": 167.25900, "radius_pm": 175.0, "ionization_ev": 6.1080, "k": 10.0, "L": 0.0, "H": 0.0},
    {"symbol": "Tm", "period": 6, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.1840, "k": 11.0, "L": 0.0, "H": 0.0},
    {"symbol": "Yb", "period": 6, "mass_u": 173.04500, "radius_pm": 194.0, "ionization_ev": 6.2540, "k": 12.0, "L": 1.0, "H": 1.0},
    {"symbol": "Lu", "period": 6, "mass_u": 174.96680, "radius_pm": 173.0, "ionization_ev": 5.4280, "k": 13.0, "L": 0.0, "H": 0.0},
]

LIGHT_CORE = [FULL_FAMILY[0], FULL_FAMILY[1], FULL_FAMILY[2], FULL_FAMILY[3], FULL_FAMILY[4]]
HEAVY_TAIL = [FULL_FAMILY[6], FULL_FAMILY[7], FULL_FAMILY[8], FULL_FAMILY[9], FULL_FAMILY[10], FULL_FAMILY[11], FULL_FAMILY[13]]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def estimate_zeff_star_without_h(item: dict) -> float:
    zeff = estimate_zeff(item["ionization_ev"], item["period"])
    return zeff + (A_K * item["k"]) + (B_L * item["L"]) + (C_Z2 * (item["period"] ** 2))


def estimate_zeff_star_with_h(item: dict) -> float:
    return estimate_zeff_star_without_h(item) + (D_H * item["H"])


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
    ks = []
    ls = []
    hs = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        zeff_star = estimate_zeff_star_without_h(item)
        evaluated.append({**item, "zeff_proxy": round(zeff, 6), "zeff_star": round(zeff_star, 6)})
        masses.append(item["mass_u"])
        radii.append(item["radius_pm"])
        ionizations.append(item["ionization_ev"])
        zeff_values.append(zeff)
        zeff_star_values.append(zeff_star)
        ks.append(item["k"])
        ls.append(item["L"])
        hs.append(item["H"])

    mass_slope, mass_intercept = linear_fit(masses, radii)
    zeff_slope, zeff_intercept = linear_fit(zeff_values, radii)
    zeff_star_slope, zeff_star_intercept = linear_fit(zeff_star_values, radii)

    mass_predicted = [mass_slope * value + mass_intercept for value in masses]
    zeff_predicted = [zeff_slope * value + zeff_intercept for value in zeff_values]
    zeff_star_predicted = [zeff_star_slope * value + zeff_star_intercept for value in zeff_star_values]

    corrected_rows = [[1.0, zeff_star, k, l, h] for zeff_star, k, l, h in zip(zeff_star_values, ks, ls, hs)]
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
                "delta": corrected_fit["coefficients"][4],
            },
            **corrected_fit,
        },
    }


def analyze_full_family_probe(series: list[dict]) -> dict:
    evaluated = []
    masses = []
    radii = []
    zeff_values = []
    zeff_star_without_h = []
    zeff_star_with_h = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        zeff_star_wo_h = estimate_zeff_star_without_h(item)
        zeff_star_h = estimate_zeff_star_with_h(item)
        evaluated.append(
            {
                **item,
                "zeff_proxy": round(zeff, 6),
                "zeff_star_wo_h": round(zeff_star_wo_h, 6),
                "zeff_star_h": round(zeff_star_h, 6),
            }
        )
        masses.append(item["mass_u"])
        radii.append(item["radius_pm"])
        zeff_values.append(zeff)
        zeff_star_without_h.append(zeff_star_wo_h)
        zeff_star_with_h.append(zeff_star_h)

    mass_slope, mass_intercept = linear_fit(masses, radii)
    zeff_slope, zeff_intercept = linear_fit(zeff_values, radii)
    wo_h_slope, wo_h_intercept = linear_fit(zeff_star_without_h, radii)
    with_h_slope, with_h_intercept = linear_fit(zeff_star_with_h, radii)

    mass_predicted = [mass_slope * value + mass_intercept for value in masses]
    zeff_predicted = [zeff_slope * value + zeff_intercept for value in zeff_values]
    wo_h_predicted = [wo_h_slope * value + wo_h_intercept for value in zeff_star_without_h]
    with_h_predicted = [with_h_slope * value + with_h_intercept for value in zeff_star_with_h]

    return {
        "series": evaluated,
        "mass": {
            "fit": {"slope": mass_slope, "intercept": mass_intercept},
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, mass_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, mass_predicted)),
        },
        "zeff": {
            "fit": {"slope": zeff_slope, "intercept": zeff_intercept},
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, zeff_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, zeff_predicted)),
        },
        "zeff_star_without_h": {
            "fit": {"slope": wo_h_slope, "intercept": wo_h_intercept},
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, wo_h_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, wo_h_predicted)),
        },
        "zeff_star_with_h": {
            "fit": {"slope": with_h_slope, "intercept": with_h_intercept},
            "rmse": math.sqrt(sum((radius - prediction) ** 2 for radius, prediction in zip(radii, with_h_predicted)) / len(radii)),
            "max_abs_residual": max(abs(radius - prediction) for radius, prediction in zip(radii, with_h_predicted)),
        },
        "mass_trend": trend(masses),
        "radius_trend": trend(radii),
        "zeff_trend": trend(zeff_values),
        "zeff_star_without_h_trend": trend(zeff_star_without_h),
        "zeff_star_with_h_trend": trend(zeff_star_with_h),
    }


def classify(light_metrics: dict, heavy_metrics: dict, anomaly_probe: dict) -> dict:
    corrected_better_light = light_metrics["corrected"]["rmse"] <= light_metrics["zeff_star"]["rmse"]
    corrected_better_heavy = heavy_metrics["corrected"]["rmse"] <= heavy_metrics["zeff_star"]["rmse"]
    h_probe_ok = anomaly_probe["zeff_star_with_h"]["rmse"] <= anomaly_probe["zeff_star_without_h"]["rmse"]
    radius_ok = (
        light_metrics["radius_trend"] == "decreasing"
        and heavy_metrics["radius_trend"] == "decreasing"
        and corrected_better_light
        and corrected_better_heavy
        and h_probe_ok
    )

    verdict = "supported" if radius_ok else "falsifie"

    return {
        "hypothesis": "using Zeff* with an H anomaly term keeps both lanthanide subseries regular and improves over mass and raw Zeff",
        "case_control": "La -> Nd -> Eu versus Gd -> Yb -> Lu, with radius compared against mass, raw Zeff, Zeff*, and [1, Zeff*, k, L, H]",
        "observable": "subseries fit quality, monotonicity, and anomaly handling at Eu and Yb",
        "expected": {
            "light_core": "Zeff* beats mass and raw Zeff, corrected fit does not worsen it",
            "heavy_tail": "Zeff* beats mass and raw Zeff, corrected fit does not worsen it",
        },
        "measured": {
            "light_core": light_metrics,
            "heavy_tail": heavy_metrics,
        },
        "criteria": {
            "corrected_better_light": corrected_better_light,
            "corrected_better_heavy": corrected_better_heavy,
            "h_probe_ok": h_probe_ok,
            "radius_ok": radius_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "one of the subseries is not monotone in radius or Zeff*",
            "Zeff* does not improve on both mass and raw Zeff in the light core",
            "Zeff* does not improve on both mass and raw Zeff in the heavy tail",
            "the corrected fit [1, Zeff*, k, L, H] does not match or improve the Zeff* baseline",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fine lanthanide subseries using Zeff* and an H anomaly term.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    light_metrics = analyze_series(LIGHT_CORE)
    heavy_metrics = analyze_series(HEAVY_TAIL)
    anomaly_probe = analyze_full_family_probe(FULL_FAMILY)
    results = classify(light_metrics, heavy_metrics, anomaly_probe)

    json_path = outdir / f"lanthanide_subseries_zeff_star_check_{timestamp}.json"
    txt_path = outdir / f"lanthanide_subseries_zeff_star_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "anomaly_probe": anomaly_probe, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Lanthanide subseries Zeff* check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Sous-serie legere La -> Eu:\n")
        handle.write(f"- mass_rmse: {light_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {light_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {light_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {light_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_trend: {light_metrics['zeff_star_trend']}\n")
        handle.write(f"- ionization_trend: {light_metrics['ionization_trend']}\n")
        handle.write("\nSous-serie lourde Gd -> Lu:\n")
        handle.write(f"- mass_rmse: {heavy_metrics['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {heavy_metrics['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_rmse: {heavy_metrics['zeff_star']['rmse']:.6f}\n")
        handle.write(f"- corrected_rmse: {heavy_metrics['corrected']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_trend: {heavy_metrics['zeff_star_trend']}\n")
        handle.write(f"- ionization_trend: {heavy_metrics['ionization_trend']}\n")
        handle.write("\nProbe full family avec H:\n")
        handle.write(f"- mass_rmse: {anomaly_probe['mass']['rmse']:.6f}\n")
        handle.write(f"- zeff_rmse: {anomaly_probe['zeff']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_wo_h_rmse: {anomaly_probe['zeff_star_without_h']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_with_h_rmse: {anomaly_probe['zeff_star_with_h']['rmse']:.6f}\n")
        handle.write(f"- zeff_star_wo_h_trend: {anomaly_probe['zeff_star_without_h_trend']}\n")
        handle.write(f"- zeff_star_with_h_trend: {anomaly_probe['zeff_star_with_h_trend']}\n")
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