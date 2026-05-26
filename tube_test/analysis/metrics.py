"""Core regression metrics."""
from __future__ import annotations

from math import log
from typing import Sequence


def rmse(residuals: Sequence[float]) -> float:
    if not residuals:
        raise ValueError("rmse requires at least one residual")
    return (sum(value * value for value in residuals) / len(residuals)) ** 0.5


def reduced_chi_square(residuals: Sequence[float], sigma: float, parameters: int) -> float:
    if len(residuals) <= parameters:
        raise ValueError("not enough data points for reduced chi-square")
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    chi2 = sum((value / sigma) ** 2 for value in residuals)
    return chi2 / (len(residuals) - parameters)


def aic(residuals: Sequence[float], parameters: int) -> float:
    if not residuals:
        raise ValueError("aic requires at least one residual")
    variance = sum(value * value for value in residuals) / len(residuals)
    variance = max(variance, 1.0e-12)
    return len(residuals) * log(variance) + 2 * parameters


def bic(residuals: Sequence[float], parameters: int) -> float:
    if not residuals:
        raise ValueError("bic requires at least one residual")
    variance = sum(value * value for value in residuals) / len(residuals)
    variance = max(variance, 1.0e-12)
    return len(residuals) * log(variance) + parameters * log(len(residuals))
