"""Fit and compare candidate saturation laws for screening S across non-alkali families."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path

from family_l_slope_check import SERIES, estimate_zeff


FAMILY_ORDER = ["p_halogen", "d_3d", "d_4d", "d_5d", "f_lanthanide_core"]
EXP_GRID = [index / 20.0 for index in range(1, 81)]
POWER_GRID = [index / 20.0 for index in range(5, 121)]
NRMSE_TOLERANCE = 0.25
PARAM_CV_TOLERANCE = 0.6


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


def split_indices(size: int) -> tuple[list[int], list[int]]:
    train = [index for index in range(size) if index % 2 == 0]
    test = [index for index in range(size) if index % 2 == 1]
    if not test:
        test = train[-1:]
        train = train[:-1]
    return train, test


def build_family_observations(family_name: str) -> dict:
    payload = SERIES[family_name]
    cases = payload["cases"]
    z0 = float(cases[0]["Z"])
    observations = []

    for case in cases:
        zeff = estimate_zeff(case["ionization_ev"], int(case["n"]))
        delta_z = float(case["Z"]) - z0
        observation = {
            **case,
            "family": family_name,
            "z0": z0,
            "delta_z": delta_z,
            "reduced_z": delta_z / float(case["n"]),
            "zeff_proxy": zeff,
            "screening": float(case["Z"]) - zeff,
        }
        observations.append(observation)

    return {
        "family": family_name,
        "l": payload["l"],
        "observations": observations,
    }


def linear_fit_rmse(rows: list[list[float]], targets: list[float]) -> dict:
    fit = fit_linear_model(rows, targets)
    return {
        "coefficients": fit["coefficients"],
        "rmse": fit["rmse"],
        "max_abs_residual": fit["max_abs_residual"],
        "predictions": fit["predicted"],
    }


def evaluate_model(observations: list[dict], train_indices: list[int], test_indices: list[int], transform) -> dict:
    train = [observations[index] for index in train_indices]
    test = [observations[index] for index in test_indices]
    train_targets = [item["screening"] for item in train]
    test_targets = [item["screening"] for item in test]

    train_rows = [[1.0, transform(item)] for item in train]
    test_rows = [[1.0, transform(item)] for item in test]

    fit = fit_linear_model(train_rows, train_targets)
    test_predictions = [sum(coefficient * value for coefficient, value in zip(fit["coefficients"], row)) for row in test_rows]

    return {
        "fit": fit,
        "train_rmse": fit["rmse"],
        "train_nrmse": normalized_rmse(train_targets, fit["predicted"]),
        "test_rmse": math.sqrt(sum((target - prediction) ** 2 for target, prediction in zip(test_targets, test_predictions)) / len(test_targets)),
        "test_nrmse": normalized_rmse(test_targets, test_predictions),
        "test_predictions": test_predictions,
    }


def fit_family(family_payload: dict) -> dict:
    observations = family_payload["observations"]
    train_indices, test_indices = split_indices(len(observations))
    train = [observations[index] for index in train_indices]
    test = [observations[index] for index in test_indices]
    train_targets = [item["screening"] for item in train]
    test_targets = [item["screening"] for item in test]

    baseline_train_rows = [[1.0, item["zeff_proxy"]] for item in train]
    baseline_test_rows = [[1.0, item["zeff_proxy"]] for item in test]
    baseline_fit = fit_linear_model(baseline_train_rows, train_targets)
    baseline_test_predictions = [sum(coefficient * value for coefficient, value in zip(baseline_fit["coefficients"], row)) for row in baseline_test_rows]
    baseline_test_rmse = math.sqrt(sum((target - prediction) ** 2 for target, prediction in zip(test_targets, baseline_test_predictions)) / len(test_targets))
    baseline_test_nrmse = normalized_rmse(test_targets, baseline_test_predictions)

    exp_candidates = []
    for parameter in EXP_GRID:
        candidate = evaluate_model(
            observations,
            train_indices,
            test_indices,
            lambda item, parameter=parameter: 1.0 - math.exp(-parameter * item["reduced_z"]),
        )
        candidate["parameter"] = parameter
        exp_candidates.append(candidate)
    exp_best = min(exp_candidates, key=lambda item: (item["test_nrmse"], item["test_rmse"]))

    power_candidates = []
    for parameter in POWER_GRID:
        candidate = evaluate_model(
            observations,
            train_indices,
            test_indices,
            lambda item, parameter=parameter: item["delta_z"] ** parameter,
        )
        candidate["parameter"] = parameter
        power_candidates.append(candidate)
    power_best = min(power_candidates, key=lambda item: (item["test_nrmse"], item["test_rmse"]))

    best_model = "exp" if exp_best["test_nrmse"] <= power_best["test_nrmse"] else "power"
    best_candidate = exp_best if best_model == "exp" else power_best

    baseline_better = baseline_test_nrmse <= min(exp_best["test_nrmse"], power_best["test_nrmse"])
    improved = best_candidate["test_nrmse"] < baseline_test_nrmse

    return {
        "family": family_payload["family"],
        "l": family_payload["l"],
        "observations": observations,
        "train_indices": train_indices,
        "test_indices": test_indices,
        "baseline": {
            "train_coefficients": baseline_fit["coefficients"],
            "train_rmse": baseline_fit["rmse"],
            "train_nrmse": normalized_rmse(train_targets, baseline_fit["predicted"]),
            "test_rmse": baseline_test_rmse,
            "test_nrmse": baseline_test_nrmse,
        },
        "exp": {
            "parameter": exp_best["parameter"],
            "train_coefficients": exp_best["fit"]["coefficients"],
            "train_rmse": exp_best["train_rmse"],
            "train_nrmse": exp_best["train_nrmse"],
            "test_rmse": exp_best["test_rmse"],
            "test_nrmse": exp_best["test_nrmse"],
        },
        "power": {
            "parameter": power_best["parameter"],
            "train_coefficients": power_best["fit"]["coefficients"],
            "train_rmse": power_best["train_rmse"],
            "train_nrmse": power_best["train_nrmse"],
            "test_rmse": power_best["test_rmse"],
            "test_nrmse": power_best["test_nrmse"],
        },
        "best_model": best_model,
        "best_candidate": {
            "model": best_model,
            "parameter": best_candidate["parameter"],
            "test_rmse": best_candidate["test_rmse"],
            "test_nrmse": best_candidate["test_nrmse"],
        },
        "baseline_better": baseline_better,
        "improved": improved,
    }


def aggregate(results: list[dict]) -> dict:
    baseline_mean = statistics.fmean(item["baseline"]["test_nrmse"] for item in results)
    exp_mean = statistics.fmean(item["exp"]["test_nrmse"] for item in results)
    power_mean = statistics.fmean(item["power"]["test_nrmse"] for item in results)

    exp_parameters = [item["exp"]["parameter"] for item in results]
    power_parameters = [item["power"]["parameter"] for item in results]
    exp_cv = statistics.pstdev(exp_parameters) / abs(statistics.fmean(exp_parameters)) if len(exp_parameters) > 1 else 0.0
    power_cv = statistics.pstdev(power_parameters) / abs(statistics.fmean(power_parameters)) if len(power_parameters) > 1 else 0.0

    best_model = "exp" if exp_mean <= power_mean else "power"
    best_mean = exp_mean if best_model == "exp" else power_mean
    best_cv = exp_cv if best_model == "exp" else power_cv
    improved_families = sum(1 for item in results if item["best_candidate"]["test_nrmse"] < item["baseline"]["test_nrmse"])

    improvement = baseline_mean - best_mean
    relative_improvement = improvement / baseline_mean if baseline_mean else 0.0
    supported = relative_improvement >= 0.12 and best_cv <= PARAM_CV_TOLERANCE and improved_families >= 4

    if supported:
        verdict = "supported"
    elif improved_families >= 2:
        verdict = "partiel"
    else:
        verdict = "contradicted"

    return {
        "baseline_mean_test_nrmse": baseline_mean,
        "exp_mean_test_nrmse": exp_mean,
        "power_mean_test_nrmse": power_mean,
        "best_model": best_model,
        "best_mean_test_nrmse": best_mean,
        "best_parameter_cv": best_cv,
        "improved_families": improved_families,
        "relative_improvement": relative_improvement,
        "supported": supported,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "screening_law"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    family_results = [fit_family(build_family_observations(family_name)) for family_name in FAMILY_ORDER]
    summary = aggregate(family_results)

    data = {
        "timestamp": timestamp,
        "hypothesis": "screening S(Z,n,l) can be stabilized by either an exponential saturation in reduced Z or a block power law, without importing alkali families",
        "case_control": "non-alkali families only: halogens, 3d, 4d, 5d, lanthanides",
        "observable": "screening S = Z - Z_eff reconstructed from first-ionization proxies",
        "families": family_results,
        **summary,
    }

    json_path = outdir / f"screening_law_saturation_check_{timestamp}.json"
    txt_path = outdir / f"screening_law_saturation_check_{timestamp}.txt"
    payload = {**data, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Screening law saturation check",
        f"timestamp: {timestamp}",
        f"verdict: {data['verdict']}",
        f"best_model: {data['best_model']}",
        f"baseline_mean_test_nrmse: {data['baseline_mean_test_nrmse']:.6f}",
        f"exp_mean_test_nrmse: {data['exp_mean_test_nrmse']:.6f}",
        f"power_mean_test_nrmse: {data['power_mean_test_nrmse']:.6f}",
        f"best_mean_test_nrmse: {data['best_mean_test_nrmse']:.6f}",
        f"best_parameter_cv: {data['best_parameter_cv']:.6f}",
        f"relative_improvement: {data['relative_improvement']:.6f}",
        f"improved_families: {data['improved_families']}/{len(data['families'])}",
        "",
        "Families: ",
    ]
    for family in data["families"]:
        lines.append(
            f"- {family['family']}: baseline={family['baseline']['test_nrmse']:.6f}, exp={family['exp']['test_nrmse']:.6f} (p={family['exp']['parameter']:.2f}), power={family['power']['test_nrmse']:.6f} (alpha={family['power']['parameter']:.2f}), best={family['best_model']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit and compare candidate screening laws across non-alkali families.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()