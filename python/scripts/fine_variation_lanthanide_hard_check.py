"""Hard validation of the fine-variation equivalence on lanthanides.

The lanthanide family is more irregular than the pnictogens. This script tests
whether a geometric fine correction and an energetic fine correction remain
locally equivalent when applied to:
- the full La -> Lu family,
- a repaired core excluding Eu and Yb,
- the heavy tail after the anomaly region.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as stats
import time
from pathlib import Path


R_H_EV = 13.6
TOLERANCE = 0.10

FULL_FAMILY = [
    {"name": "La", "period": 6, "radius_pm": 195.0, "ionization_ev": 5.5770},
    {"name": "Ce", "period": 6, "radius_pm": 185.0, "ionization_ev": 5.5387},
    {"name": "Pr", "period": 6, "radius_pm": 182.0, "ionization_ev": 5.4730},
    {"name": "Nd", "period": 6, "radius_pm": 181.0, "ionization_ev": 5.5250},
    {"name": "Sm", "period": 6, "radius_pm": 180.0, "ionization_ev": 5.6440},
    {"name": "Eu", "period": 6, "radius_pm": 199.0, "ionization_ev": 5.6700},
    {"name": "Gd", "period": 6, "radius_pm": 180.0, "ionization_ev": 6.1500},
    {"name": "Tb", "period": 6, "radius_pm": 178.0, "ionization_ev": 5.8630},
    {"name": "Dy", "period": 6, "radius_pm": 177.0, "ionization_ev": 5.9390},
    {"name": "Ho", "period": 6, "radius_pm": 176.0, "ionization_ev": 6.0220},
    {"name": "Er", "period": 6, "radius_pm": 175.0, "ionization_ev": 6.1080},
    {"name": "Tm", "period": 6, "radius_pm": 174.0, "ionization_ev": 6.1840},
    {"name": "Yb", "period": 6, "radius_pm": 194.0, "ionization_ev": 6.2540},
    {"name": "Lu", "period": 6, "radius_pm": 173.0, "ionization_ev": 5.4280},
]

REPAIRED_CORE = [item for item in FULL_FAMILY if item["name"] not in {"Eu", "Yb"}]
HEAVY_TAIL = [item for item in FULL_FAMILY if item["name"] not in {"La", "Ce", "Pr", "Nd", "Sm"}]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = stats.fmean(xs)
    mean_y = stats.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def rmse(y_values: list[float], y_pred: list[float]) -> float:
    return math.sqrt(sum((y - yhat) ** 2 for y, yhat in zip(y_values, y_pred)) / len(y_values))


def normalized_rmse(y_values: list[float], y_pred: list[float]) -> float:
    spread = max(y_values) - min(y_values)
    if spread == 0:
        return 0.0
    return rmse(y_values, y_pred) / spread


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            return [0.0] * size
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
    return {
        "coefficients": coefficients,
        "predicted": predicted,
        "rmse": rmse(targets, predicted),
        "nrmse": normalized_rmse(targets, predicted),
    }


def evaluate_family(series: list[dict]) -> dict:
    radius = [float(item["radius_pm"]) for item in series]
    period = [float(item["period"]) for item in series]
    ie = [float(item["ionization_ev"]) for item in series]
    zeff_proxy = [math.sqrt((value * p * p) / R_H_EV) for value, p in zip(ie, period)]
    geometric_proxy = [1.0 / p for p in period]
    energetic_proxy = ie

    base_slope, base_intercept = linear_fit(zeff_proxy, radius)
    base_pred = [base_slope * x + base_intercept for x in zeff_proxy]
    base_nrmse = normalized_rmse(radius, base_pred)

    geo_rows = [[1.0, z, g] for z, g in zip(zeff_proxy, geometric_proxy)]
    ene_rows = [[1.0, z, e] for z, e in zip(zeff_proxy, energetic_proxy)]

    geo_fit = fit_multivariate(geo_rows, radius)
    ene_fit = fit_multivariate(ene_rows, radius)

    geo_gain = base_nrmse - geo_fit["nrmse"]
    ene_gain = base_nrmse - ene_fit["nrmse"]
    gap = abs(geo_gain - ene_gain)

    return {
        "series": [item["name"] for item in series],
        "baseline_nrmse": base_nrmse,
        "geometric_nrmse": geo_fit["nrmse"],
        "energetic_nrmse": ene_fit["nrmse"],
        "geometric_gain": geo_gain,
        "energetic_gain": ene_gain,
        "gain_gap": gap,
        "equivalent": gap <= TOLERANCE and geo_gain > 0 and ene_gain > 0,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    families = {
        "lanthanide_full": evaluate_family(FULL_FAMILY),
        "lanthanide_repaired_core": evaluate_family(REPAIRED_CORE),
        "lanthanide_heavy_tail": evaluate_family(HEAVY_TAIL),
    }

    equivalent = all(result["equivalent"] for result in families.values())
    verdict = "supported" if equivalent else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "equivalent": equivalent,
        "tolerance": TOLERANCE,
        "families": families,
    }

    json_path = outdir / f"fine_variation_lanthanide_hard_check_{timestamp}.json"
    txt_path = outdir / f"fine_variation_lanthanide_hard_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Fine variation lanthanide hard check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"equivalent: {equivalent}",
        f"tolerance: {TOLERANCE}",
        "",
    ]
    for label, family in families.items():
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
    parser = argparse.ArgumentParser(description="Hard validation of the fine-variation equivalence on lanthanides.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()