"""Leave-one-out validation of the fine-variation model on the boron family.

This is a harder check than a single family fit:
- each boron-family element is held out once,
- the model is trained on the remaining 4 points,
- two regressors are compared on the held-out point: mass and raw Z_eff.

The hypothesis is supported only if raw Z_eff generalizes better than mass
across the leave-one-out sweep.
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
    {"symbol": "B", "period": 2, "mass_u": 10.81, "radius_pm": 87.0, "ionization_ev": 8.298, "k": 0.0, "L": 0.0},
    {"symbol": "Al", "period": 3, "mass_u": 26.9815385, "radius_pm": 143.0, "ionization_ev": 5.9858, "k": 1.0, "L": 0.0},
    {"symbol": "Ga", "period": 4, "mass_u": 69.723, "radius_pm": 135.0, "ionization_ev": 5.9993, "k": 2.0, "L": 1.0},
    {"symbol": "In", "period": 5, "mass_u": 114.818, "radius_pm": 156.0, "ionization_ev": 5.7864, "k": 3.0, "L": 0.0},
    {"symbol": "Tl", "period": 6, "mass_u": 204.38, "radius_pm": 170.0, "ionization_ev": 6.1082, "k": 4.0, "L": 1.0},
]

ALPHA = 0.0
BETA = 0.0


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


def build_rows(sample: dict) -> dict[str, list[float]]:
    zeff = estimate_zeff(sample["ionization_ev"], sample["period"])
    return {
        "mass": [1.0, sample["mass_u"]],
        "zeff": [1.0, zeff],
        "radius": sample["radius_pm"],
    }


def run_leave_one_out() -> dict:
    fold_results = []
    total_errors = {"mass": [], "zeff": []}

    for held_out_index, held_out in enumerate(FAMILY):
        train = [sample for index, sample in enumerate(FAMILY) if index != held_out_index]
        train_rows = [build_rows(sample) for sample in train]
        held_out_rows = build_rows(held_out)

        targets = [row["radius"] for row in train_rows]
        model_specs = {
            "mass": [row["mass"] for row in train_rows],
            "zeff": [row["zeff"] for row in train_rows],
        }
        coefficients = {name: fit_ridge(rows, targets) for name, rows in model_specs.items()}

        errors = {}
        for name, coeffs in coefficients.items():
            pred = predict(coeffs, held_out_rows[name])
            errors[name] = (pred - held_out_rows["radius"]) ** 2
            total_errors[name].append(errors[name])

        fold_results.append(
            {
                "held_out": held_out["symbol"],
                "mass_error": errors["mass"],
                "zeff_error": errors["zeff"],
                "best_model": min(errors, key=errors.get),
            }
        )

    rmses = {name: math.sqrt(sum(values) / len(values)) for name, values in total_errors.items()}
    supported = rmses["zeff"] < rmses["mass"]

    return {
        "overall_verdict": "supported" if supported else "contradicted",
        "family": [sample["symbol"] for sample in FAMILY],
        "folds": fold_results,
        "summary": {
            "mass_rmse": rmses["mass"],
            "zeff_rmse": rmses["zeff"],
            "best_model": min(rmses, key=rmses.get),
        },
        "hypothesis": "leave-one-out on the boron family is best explained by raw Z_eff rather than mass",
        "case_control": "full B -> Tl family with each element held out once",
        "observable": "held-out radius prediction error across mass and raw Z_eff",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Leave-one-out validation of the fine-variation model on the boron family.")
    _ = parser.parse_args()

    results_dir = Path(__file__).resolve().parents[1] / "results"
    results_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    results = run_leave_one_out()

    json_path = results_dir / f"fine_variation_boron_loo_check_{timestamp}.json"
    txt_path = results_dir / f"fine_variation_boron_loo_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Fine variation boron leave-one-out check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Hypothesis: {results['hypothesis']}\n")
        handle.write(f"Case control: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['overall_verdict']}\n")
        handle.write(f"Mass RMSE: {results['summary']['mass_rmse']:.6f}\n")
        handle.write(f"Zeff RMSE: {results['summary']['zeff_rmse']:.6f}\n")
        handle.write(f"Best model: {results['summary']['best_model']}\n\n")
        for fold in results["folds"]:
            handle.write(f"Held out: {fold['held_out']}\n")
            handle.write(f"  mass error: {fold['mass_error']:.6f}\n")
            handle.write(f"  zeff error: {fold['zeff_error']:.6f}\n")
            handle.write(f"  best model: {fold['best_model']}\n\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()