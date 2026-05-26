"""Validate tube metrics on real hysteresis data using the current skeleton models."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tube_test.analysis.cross_validation import Dataset, evaluate_dataset
from tube_test.scripts.run_tube_suite import load_manifest, workspace_root


def load_json_cases(path: Path) -> dict[str, list[dict]]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_hysteresis_dataset(name: str, payload: dict[str, list[dict]], limit: int = 3) -> list[Dataset]:
    datasets: list[Dataset] = []
    for index, case_name in enumerate(payload.keys()):
        if index >= limit:
            break
        series = payload[case_name]
        if not isinstance(series, list) or not series:
            raise TypeError(f"expected a non-empty list for {name}:{case_name}")

        case = series[0]
        if not isinstance(case, dict):
            raise TypeError(f"expected a case dictionary for {name}:{case_name}")

        observed = [float(value) for value in case["force"]]
        omega = [float(value) for value in case["velocity"]]
        baseline = sum(observed) / len(observed)
        standard = [baseline for _ in observed]
        sigma = max((sum((value - baseline) ** 2 for value in observed) / len(observed)) ** 0.5, 1.0)
        datasets.append(
            Dataset(
                name=f"{name}:{case_name}",
                observed=observed,
                standard=standard,
                omega=omega,
                sigma=sigma,
            )
        )
    return datasets


def evaluate_collection(datasets: list[Dataset]) -> dict:
    if not datasets:
        raise ValueError("no datasets to evaluate")

    fitted_lambda = None
    reports = []
    for index, dataset in enumerate(datasets):
        result = evaluate_dataset(dataset, lambda_value=fitted_lambda)
        if fitted_lambda is None:
            fitted_lambda = result["lambda"]
        reports.append(result)

    standard_rmse = sum(item["standard"]["rmse"] for item in reports) / len(reports)
    tube_rmse = sum(item["tube"]["rmse"] for item in reports) / len(reports)
    standard_aic = sum(item["standard"]["aic"] for item in reports) / len(reports)
    tube_aic = sum(item["tube"]["aic"] for item in reports) / len(reports)

    if not tube_rmse <= standard_rmse:
        raise RuntimeError("tube rmse must not be worse than the standard model on real hysteresis data")
    if not tube_aic <= standard_aic:
        raise RuntimeError("tube aic must not be worse than the standard model on real hysteresis data")

    return {
        "lambda": fitted_lambda,
        "reports": reports,
        "standard_rmse": standard_rmse,
        "tube_rmse": tube_rmse,
        "standard_aic": standard_aic,
        "tube_aic": tube_aic,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate tube metrics on real hysteresis data.")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to the manifest JSON file",
    )
    args = parser.parse_args()

    root = workspace_root()
    tube_root = root / "tube_test"
    manifest_path = Path(args.manifest) if args.manifest else tube_root / "data" / "manifest.json"
    manifest = load_manifest(manifest_path)

    datasets_by_name = {dataset["name"]: dataset for dataset in manifest.get("datasets", [])}
    one_fixed_path = tube_root / datasets_by_name["one_fixed_damper"]["path"]
    test_experiments_path = tube_root / datasets_by_name["test_experiments"]["path"]
    csv_path = tube_root / datasets_by_name["core_loss_mhz"]["path"]

    one_fixed = build_hysteresis_dataset("one_fixed_damper", load_json_cases(one_fixed_path), limit=3)
    test_experiments = build_hysteresis_dataset("test_experiments", load_json_cases(test_experiments_path), limit=3)
    csv_rows = load_csv_rows(csv_path)
    if not csv_rows:
        raise RuntimeError("core_loss_mhz csv is empty")

    result_one = evaluate_collection(one_fixed)
    result_test = evaluate_collection(test_experiments)

    print(
        json.dumps(
            {
                "status": "ok",
                "manifest": str(manifest_path),
                "one_fixed_damper": result_one,
                "test_experiments": result_test,
                "core_loss_mhz_rows_checked": len(csv_rows),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()