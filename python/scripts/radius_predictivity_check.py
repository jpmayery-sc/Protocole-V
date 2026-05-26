"""Check non-retrofit radius prediction with held-out families."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path

from core_valence_correction_check import FAMILIES, estimate_zeff


FAMILY_ORDER = ["alkali", "halogen", "transition_3d", "transition_4d", "transition_5d", "lanthanide"]
TEST_TOLERANCE = 0.15


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


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


def fit_linear_model(rows: list[list[float]], targets: list[float]) -> dict:
    columns = len(rows[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]

    for row, target in zip(rows, targets):
        for i in range(columns):
            xty[i] += row[i] * target
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]

    regularization = 1.0e-9
    for index in range(columns):
        xtx[index][index] += regularization

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


def normalized_rmse(values: list[float], predictions: list[float]) -> float:
    spread = max(values) - min(values)
    if spread == 0.0:
        return 0.0
    rmse = math.sqrt(sum((value - prediction) ** 2 for value, prediction in zip(values, predictions)) / len(values))
    return rmse / spread


def build_family(name: str) -> dict:
    family = FAMILIES[name]
    l_valence = float(family["l_valence"])
    l_core = float(family["l_core"])
    observations = []
    for item in family["items"]:
        zeff = estimate_zeff(item["ionization_ev"], int(item["period"]))
        observations.append({
            **item,
            "family": name,
            "l_valence": l_valence,
            "l_core": l_core,
            "zeff_proxy": zeff,
        })
    return {
        "family": name,
        "l_valence": l_valence,
        "l_core": l_core,
        "observations": observations,
    }


def family_rows(records: list[dict], *, corrected: bool) -> list[list[float]]:
    if corrected:
        return [[1.0, item["zeff_proxy"], item["l_valence"], item["l_core"]] for item in records]
    return [[1.0, item["zeff_proxy"]] for item in records]


def family_prediction(records: list[dict], coefficients: list[float], *, corrected: bool) -> list[float]:
    rows = family_rows(records, corrected=corrected)
    return [sum(coefficient * value for coefficient, value in zip(coefficients, row)) for row in rows]


def evaluate_family(test_name: str) -> dict:
    training_names = [name for name in FAMILY_ORDER if name != test_name]
    training_records = []
    for name in training_names:
        training_records.extend(build_family(name)["observations"])
    test_family = build_family(test_name)
    test_records = test_family["observations"]

    train_targets = [item["radius_pm"] for item in training_records]
    test_targets = [item["radius_pm"] for item in test_records]

    baseline_fit = fit_linear_model(family_rows(training_records, corrected=False), train_targets)
    corrected_fit = fit_linear_model(family_rows(training_records, corrected=True), train_targets)

    baseline_predictions = family_prediction(test_records, baseline_fit["coefficients"], corrected=False)
    corrected_predictions = family_prediction(test_records, corrected_fit["coefficients"], corrected=True)

    baseline_test_rmse = math.sqrt(sum((target - prediction) ** 2 for target, prediction in zip(test_targets, baseline_predictions)) / len(test_targets))
    corrected_test_rmse = math.sqrt(sum((target - prediction) ** 2 for target, prediction in zip(test_targets, corrected_predictions)) / len(test_targets))

    baseline_test_nrmse = normalized_rmse(test_targets, baseline_predictions)
    corrected_test_nrmse = normalized_rmse(test_targets, corrected_predictions)

    return {
        "family": test_name,
        "l_valence": test_family["l_valence"],
        "l_core": test_family["l_core"],
        "baseline": {
            "train_rmse": baseline_fit["rmse"],
            "train_nrmse": normalized_rmse(train_targets, baseline_fit["predicted"]),
            "test_rmse": baseline_test_rmse,
            "test_nrmse": baseline_test_nrmse,
        },
        "corrected": {
            "train_rmse": corrected_fit["rmse"],
            "train_nrmse": normalized_rmse(train_targets, corrected_fit["predicted"]),
            "test_rmse": corrected_test_rmse,
            "test_nrmse": corrected_test_nrmse,
        },
        "improved": corrected_test_nrmse < baseline_test_nrmse,
        "relative_improvement": (baseline_test_nrmse - corrected_test_nrmse) / baseline_test_nrmse if baseline_test_nrmse else 0.0,
    }


def aggregate(results: list[dict]) -> dict:
    baseline_mean = statistics.fmean(item["baseline"]["test_nrmse"] for item in results)
    corrected_mean = statistics.fmean(item["corrected"]["test_nrmse"] for item in results)
    improved_families = sum(1 for item in results if item["improved"])
    relative_improvement = (baseline_mean - corrected_mean) / baseline_mean if baseline_mean else 0.0
    supported = relative_improvement >= TEST_TOLERANCE and improved_families >= 3
    verdict = "supported" if supported else ("partiel" if improved_families >= 2 else "contradicted")

    return {
        "baseline_mean_test_nrmse": baseline_mean,
        "corrected_mean_test_nrmse": corrected_mean,
        "improved_families": improved_families,
        "relative_improvement": relative_improvement,
        "supported": supported,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "radius_predictivity"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    family_results = [evaluate_family(name) for name in FAMILY_ORDER]
    summary = aggregate(family_results)

    data = {
        "timestamp": timestamp,
        "hypothesis": "a held-out radius model with explicit core/valence terms should improve over Zeff-only prediction without retrofitting the test family",
        "case_control": "leave-one-family-out over alkali, halogen, 3d, 4d, 5d and lanthanide families",
        "observable": "atomic radius prediction error",
        "families": family_results,
        **summary,
    }

    json_path = outdir / f"radius_predictivity_check_{timestamp}.json"
    txt_path = outdir / f"radius_predictivity_check_{timestamp}.txt"
    payload = {**data, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Radius predictivity check",
        f"timestamp: {timestamp}",
        f"verdict: {data['verdict']}",
        f"baseline_mean_test_nrmse: {data['baseline_mean_test_nrmse']:.6f}",
        f"corrected_mean_test_nrmse: {data['corrected_mean_test_nrmse']:.6f}",
        f"relative_improvement: {data['relative_improvement']:.6f}",
        f"improved_families: {data['improved_families']}/{len(data['families'])}",
        "",
        "Families:",
    ]
    for family in data["families"]:
        lines.append(
            f"- {family['family']}: baseline={family['baseline']['test_nrmse']:.6f}, corrected={family['corrected']['test_nrmse']:.6f}, improved={family['improved']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check non-retrofit atomic radius predictivity.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()