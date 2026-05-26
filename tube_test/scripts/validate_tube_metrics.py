"""Validate the tube metrics on a synthetic case."""
from __future__ import annotations

import json

from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tube_test.analysis.cross_validation import Dataset, evaluate_dataset


def build_reference_dataset() -> Dataset:
    omega = [-2.0, -1.0, 0.0, 1.0, 2.0]
    standard = [10.0, 10.0, 10.0, 10.0, 10.0]
    lambda_true = 0.25
    observed = [base + lambda_true * value for base, value in zip(standard, omega)]
    return Dataset(
        name="synthetic_tube_case",
        observed=observed,
        standard=standard,
        omega=omega,
        sigma=1.0,
    )


def main() -> None:
    dataset = build_reference_dataset()
    result = evaluate_dataset(dataset)

    standard = result["standard"]
    tube = result["tube"]

    if not tube["rmse"] < standard["rmse"]:
        raise RuntimeError("tube rmse must improve on the synthetic case")
    if not tube["aic"] < standard["aic"]:
        raise RuntimeError("tube aic must improve on the synthetic case")
    if not tube["bic"] < standard["bic"]:
        raise RuntimeError("tube bic must improve on the synthetic case")
    if not tube["chi2_red"] < standard["chi2_red"]:
        raise RuntimeError("tube chi2_red must improve on the synthetic case")

    print(
        json.dumps(
            {
                "status": "ok",
                "name": result["name"],
                "lambda": result["lambda"],
                "standard": standard,
                "tube": tube,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()