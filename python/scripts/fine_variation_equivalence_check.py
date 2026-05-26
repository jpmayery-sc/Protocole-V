"""Validate the fine-variation hypothesis as a distance/energy equivalence.

Electron-5 states that a fine variation of e-p distance and a fine variation of
energy loss are two views of the same small delta Z_eff. This check compares two
parametrizations of the same residual on two same-valence families:
- geometric proxy: 1 / principal shell number
- energetic proxy: first ionization energy

If both parametrizations improve the same baseline fit by a similar amount, the
equivalence is supported; if one dominates clearly, the hypotheses are treated
as distinguishable on this data.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as stats
import time
from pathlib import Path


ALKALI = [
    {"name": "Li", "period": 2, "radius_pm": 152, "ie_ev": 5.39},
    {"name": "Na", "period": 3, "radius_pm": 186, "ie_ev": 5.14},
    {"name": "K", "period": 4, "radius_pm": 227, "ie_ev": 4.34},
    {"name": "Rb", "period": 5, "radius_pm": 248, "ie_ev": 4.18},
    {"name": "Cs", "period": 6, "radius_pm": 267, "ie_ev": 3.89},
]

HALOGENS = [
    {"name": "F", "period": 2, "radius_pm": 50, "ie_ev": 17.42},
    {"name": "Cl", "period": 3, "radius_pm": 79, "ie_ev": 12.97},
    {"name": "Br", "period": 4, "radius_pm": 94, "ie_ev": 11.81},
    {"name": "I", "period": 5, "radius_pm": 115, "ie_ev": 10.45},
    {"name": "At", "period": 6, "radius_pm": 133, "ie_ev": 9.30},
]

EQUIVALENCE_TOLERANCE = 0.15


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def linear_fit(x_values: list[float], y_values: list[float]) -> tuple[float, float]:
    x_mean = stats.mean(x_values)
    y_mean = stats.mean(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


def rmse(y_values: list[float], y_pred: list[float]) -> float:
    return math.sqrt(sum((y - yhat) ** 2 for y, yhat in zip(y_values, y_pred)) / len(y_values))


def normalized_rmse(y_values: list[float], y_pred: list[float]) -> float:
    spread = max(y_values) - min(y_values)
    if spread == 0:
        return 0.0
    return rmse(y_values, y_pred) / spread


def evaluate_family(series: list[dict]) -> dict:
    radius = [float(item["radius_pm"]) for item in series]
    period = [float(item["period"]) for item in series]
    ie = [float(item["ie_ev"]) for item in series]
    zeff_proxy = [math.sqrt((value * p * p) / 13.6) for value, p in zip(ie, period)]
    geometric_proxy = [1.0 / p for p in period]
    energetic_proxy = ie

    base_slope, base_intercept = linear_fit(zeff_proxy, radius)
    base_pred = [base_slope * x + base_intercept for x in zeff_proxy]
    base_nrmse = normalized_rmse(radius, base_pred)

    geo_rows = [[1.0, z, g] for z, g in zip(zeff_proxy, geometric_proxy)]
    ene_rows = [[1.0, z, e] for z, e in zip(zeff_proxy, energetic_proxy)]

    geo_beta = solve_least_squares(geo_rows, radius)
    ene_beta = solve_least_squares(ene_rows, radius)

    geo_pred = [row[0] * geo_beta[0] + row[1] * geo_beta[1] + row[2] * geo_beta[2] for row in geo_rows]
    ene_pred = [row[0] * ene_beta[0] + row[1] * ene_beta[1] + row[2] * ene_beta[2] for row in ene_rows]

    geo_nrmse = normalized_rmse(radius, geo_pred)
    ene_nrmse = normalized_rmse(radius, ene_pred)

    geo_gain = base_nrmse - geo_nrmse
    ene_gain = base_nrmse - ene_nrmse
    gap = abs(geo_gain - ene_gain)

    return {
        "series": [item["name"] for item in series],
        "baseline_nrmse": base_nrmse,
        "geometric_nrmse": geo_nrmse,
        "energetic_nrmse": ene_nrmse,
        "geometric_gain": geo_gain,
        "energetic_gain": ene_gain,
        "gain_gap": gap,
        "equivalent": gap <= EQUIVALENCE_TOLERANCE and geo_gain > 0 and ene_gain > 0,
        "items": series,
    }


def solve_least_squares(rows: list[list[float]], y_values: list[float]) -> list[float]:
    size = len(rows[0])
    gram = [[0.0 for _ in range(size)] for _ in range(size)]
    rhs = [0.0 for _ in range(size)]
    for row, y in zip(rows, y_values):
        for i in range(size):
            rhs[i] += row[i] * y
            for j in range(size):
                gram[i][j] += row[i] * row[j]
    return gaussian_elimination(gram, rhs)


def gaussian_elimination(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    a = [row[:] for row in matrix]
    b = vector[:]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) < 1e-12:
            return [0.0] * n
        a[col], a[pivot] = a[pivot], a[col]
        b[col], b[pivot] = b[pivot], b[col]
        pivot_value = a[col][col]
        for j in range(col, n):
            a[col][j] /= pivot_value
        b[col] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            for j in range(col, n):
                a[row][j] -= factor * a[col][j]
            b[row] -= factor * b[col]
    return b


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    alkali = evaluate_family(ALKALI)
    halogens = evaluate_family(HALOGENS)

    equivalent = alkali["equivalent"] and halogens["equivalent"]
    verdict = "supported" if equivalent else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "equivalent": equivalent,
        "tolerance": EQUIVALENCE_TOLERANCE,
        "families": {
            "alkali": alkali,
            "halogens": halogens,
        },
    }

    json_path = outdir / f"fine_variation_equivalence_check_{timestamp}.json"
    txt_path = outdir / f"fine_variation_equivalence_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Fine variation equivalence check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"equivalent: {equivalent}",
        f"tolerance: {EQUIVALENCE_TOLERANCE}",
        "",
    ]
    for label, family in data["families"].items():
        lines.append(f"{label}:")
        lines.append(f"- baseline_nrmse: {family['baseline_nrmse']:.6f}")
        lines.append(f"- geometric_nrmse: {family['geometric_nrmse']:.6f}")
        lines.append(f"- energetic_nrmse: {family['energetic_nrmse']:.6f}")
        lines.append(f"- geometric_gain: {family['geometric_gain']:.6f}")
        lines.append(f"- energetic_gain: {family['energetic_gain']:.6f}")
        lines.append(f"- gain_gap: {family['gain_gap']:.6f}")
        lines.append(f"- equivalent: {family['equivalent']}")
        lines.append(f"- series: {', '.join(family['series'])}")
        lines.append("")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the fine-variation equivalence hypothesis.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()