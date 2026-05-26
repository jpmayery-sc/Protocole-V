"""Simple cross-validation helpers for the tube series."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from tube_test.analysis.fit_lambda import fit_lambda
from tube_test.analysis.metrics import aic, bic, reduced_chi_square, rmse
from tube_test.models.model_tube import apply_tube_correction


@dataclass(frozen=True)
class Dataset:
    name: str
    observed: Sequence[float]
    standard: Sequence[float]
    omega: Sequence[float]
    sigma: float


def evaluate_dataset(dataset: Dataset, lambda_value: float | None = None) -> dict:
    standard_residuals = [obs - std for obs, std in zip(dataset.observed, dataset.standard)]
    fitted_lambda = lambda_value if lambda_value is not None else fit_lambda(standard_residuals, dataset.omega)
    tube_prediction = apply_tube_correction(dataset.standard, dataset.omega, fitted_lambda)
    tube_residuals = [obs - pred for obs, pred in zip(dataset.observed, tube_prediction)]

    return {
        "name": dataset.name,
        "lambda": fitted_lambda,
        "standard": {
            "rmse": rmse(standard_residuals),
            "aic": aic(standard_residuals, 1),
            "bic": bic(standard_residuals, 1),
            "chi2_red": reduced_chi_square(standard_residuals, dataset.sigma, 1),
        },
        "tube": {
            "rmse": rmse(tube_residuals),
            "aic": aic(tube_residuals, 2),
            "bic": bic(tube_residuals, 2),
            "chi2_red": reduced_chi_square(tube_residuals, dataset.sigma, 2),
        },
    }
