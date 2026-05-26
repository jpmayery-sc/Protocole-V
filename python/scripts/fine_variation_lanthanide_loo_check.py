"""Leave-one-out hard validation of the fine-variation model on lanthanides.

This is a stricter test than the subseries split:
- each lanthanide is held out once,
- the model is trained on the remaining 13 points,
- three regressors are compared on the held-out point:
    mass, raw Z_eff, and a reduced Zeff* without the H anomaly term.

The hypothesis is supported only if the reduced Zeff* generalizes better than
the simpler baselines across the full leave-one-out sweep.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as stats
import time
from pathlib import Path


R_H_EV = 13.6
RIDGE = 1e-6

FAMILY = [
    {"symbol": "La", "period": 6, "Z": 57, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.5770, "k": 0.0, "L": 0.0, "H": 0.0},
    {"symbol": "Ce", "period": 6, "Z": 58, "mass_u": 140.11600, "radius_pm": 185.0, "ionization_ev": 5.5387, "k": 1.0, "L": 0.0, "H": 0.0},
    {"symbol": "Pr", "period": 6, "Z": 59, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.4730, "k": 2.0, "L": 0.0, "H": 0.0},
    {"symbol": "Nd", "period": 6, "Z": 60, "mass_u": 144.24200, "radius_pm": 181.0, "ionization_ev": 5.5250, "k": 3.0, "L": 0.0, "H": 0.0},
    {"symbol": "Sm", "period": 6, "Z": 62, "mass_u": 150.36000, "radius_pm": 180.0, "ionization_ev": 5.6440, "k": 4.0, "L": 0.0, "H": 0.0},
    {"symbol": "Eu", "period": 6, "Z": 63, "mass_u": 151.96400, "radius_pm": 199.0, "ionization_ev": 5.6700, "k": 5.0, "L": 1.0, "H": 1.0},
    {"symbol": "Gd", "period": 6, "Z": 64, "mass_u": 157.25000, "radius_pm": 180.0, "ionization_ev": 6.1500, "k": 6.0, "L": 0.0, "H": 0.0},
    {"symbol": "Tb", "period": 6, "Z": 65, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.8630, "k": 7.0, "L": 0.0, "H": 0.0},
    {"symbol": "Dy", "period": 6, "Z": 66, "mass_u": 162.50000, "radius_pm": 177.0, "ionization_ev": 5.9390, "k": 8.0, "L": 0.0, "H": 0.0},
    {"symbol": "Ho", "period": 6, "Z": 67, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.0220, "k": 9.0, "L": 0.0, "H": 0.0},
    {"symbol": "Er", "period": 6, "Z": 68, "mass_u": 167.25900, "radius_pm": 175.0, "ionization_ev": 6.1080, "k": 10.0, "L": 0.0, "H": 0.0},
    {"symbol": "Tm", "period": 6, "Z": 69, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.1840, "k": 11.0, "L": 0.0, "H": 0.0},
    {"symbol": "Yb", "period": 6, "Z": 70, "mass_u": 173.04500, "radius_pm": 194.0, "ionization_ev": 6.2540, "k": 12.0, "L": 1.0, "H": 1.0},
    {"symbol": "Lu", "period": 6, "Z": 71, "mass_u": 174.96680, "radius_pm": 173.0, "ionization_ev": 5.4280, "k": 13.0, "L": 0.0, "H": 0.0},
]

ALPHA = 0.0
BETA = 0.25
GAMMA = 1.1e-4


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


def fit_ridge(rows: list[list[float]], targets: list[float], ridge: float = RIDGE) -> list[float]:
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

    return solve_linear_system(xtx, xty)


def predict(coefficients: list[float], row: list[float]) -> float:
    return sum(coefficient * value for coefficient, value in zip(coefficients, row))


def squared_error(predicted: float, target: float) -> float:
    return (predicted - target) ** 2


def build_rows(sample: dict) -> dict[str, list[float]]:
    zeff = estimate_zeff(sample["ionization_ev"], sample["period"])
    zeff_star = zeff + ALPHA * sample["k"] + BETA * sample["L"] + GAMMA * (sample["Z"] ** 2)
    return {
        "mass": [1.0, sample["mass_u"]],
        "zeff": [1.0, zeff],
        "zeff_star": [1.0, zeff, sample["k"], sample["L"]],
        "radius": sample["radius_pm"],
        "zeff_value": zeff,
        "zeff_star_value": zeff_star,
    }


def run_leave_one_out() -> dict:
    fold_results = []
    total_errors = {
        "mass": [],
        "zeff": [],
        "zeff_star": [],
    }

    for held_out_index, held_out in enumerate(FAMILY):
        train = [sample for index, sample in enumerate(FAMILY) if index != held_out_index]
        train_rows = [build_rows(sample) for sample in train]
        held_out_rows = build_rows(held_out)

        model_specs = {
            "mass": [row["mass"] for row in train_rows],
            "zeff": [row["zeff"] for row in train_rows],
            "zeff_star": [row["zeff_star"] for row in train_rows],
        }

        targets = [row["radius"] for row in train_rows]
        coefficients = {name: fit_ridge(rows, targets) for name, rows in model_specs.items()}

        errors = {}
        for name, coeffs in coefficients.items():
            pred = predict(coeffs, held_out_rows[name])
            errors[name] = squared_error(pred, held_out_rows["radius"])
            total_errors[name].append(errors[name])

        fold_results.append(
            {
                "held_out": held_out["symbol"],
                "radius": held_out["radius_pm"],
                "mass_error": errors["mass"],
                "zeff_error": errors["zeff"],
                "zeff_star_error": errors["zeff_star"],
                "best_model": min(errors, key=errors.get),
            }
        )

    rmse = {name: math.sqrt(sum(values) / len(values)) for name, values in total_errors.items()}
    rmses = rmse

    supported = rmses["zeff_star"] < rmses["mass"] and rmses["zeff_star"] < rmses["zeff"]

    return {
        "overall_verdict": "supported" if supported else "contradicted",
        "family": [sample["symbol"] for sample in FAMILY],
        "folds": fold_results,
        "summary": {
            "mass_rmse": rmses["mass"],
            "zeff_rmse": rmses["zeff"],
            "zeff_star_rmse": rmses["zeff_star"],
            "best_model": min(rmses, key=rmses.get),
        },
        "hypothesis": "leave-one-out on lanthanides is best explained by Zeff* without the H anomaly term rather than mass or raw Zeff",
        "case_control": "full La -> Lu family with each element held out once",
        "observable": "held-out radius prediction error across three model classes",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Leave-one-out hard validation of the fine-variation model on lanthanides.")
    _ = parser.parse_args()

    results_dir = Path(__file__).resolve().parents[1] / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    results = run_leave_one_out()

    json_path = results_dir / f"fine_variation_lanthanide_loo_check_{timestamp}.json"
    txt_path = results_dir / f"fine_variation_lanthanide_loo_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Fine variation lanthanide leave-one-out check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Hypothesis: {results['hypothesis']}\n")
        handle.write(f"Case control: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['overall_verdict']}\n")
        handle.write(f"Mass RMSE: {results['summary']['mass_rmse']:.6f}\n")
        handle.write(f"Zeff RMSE: {results['summary']['zeff_rmse']:.6f}\n")
        handle.write(f"Zeff* RMSE: {results['summary']['zeff_star_rmse']:.6f}\n")
        handle.write(f"Best model: {results['summary']['best_model']}\n\n")
        for fold in results["folds"]:
            handle.write(f"Held out: {fold['held_out']}\n")
            handle.write(f"  radius: {fold['radius']:.3f}\n")
            handle.write(f"  mass error: {fold['mass_error']:.6f}\n")
            handle.write(f"  zeff error: {fold['zeff_error']:.6f}\n")
            handle.write(f"  zeff* error: {fold['zeff_star_error']:.6f}\n")
            handle.write(f"  best model: {fold['best_model']}\n\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()