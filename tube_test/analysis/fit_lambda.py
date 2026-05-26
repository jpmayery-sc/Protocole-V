"""Least-squares fit for the single tube coefficient."""
from __future__ import annotations

from typing import Sequence


def fit_lambda(residuals: Sequence[float], omega_values: Sequence[float]) -> float:
    if len(residuals) != len(omega_values):
        raise ValueError("residuals and omega_values must have the same length")

    numerator = sum(residual * omega for residual, omega in zip(residuals, omega_values))
    denominator = sum(omega * omega for omega in omega_values)
    if denominator == 0.0:
        raise ValueError("omega_values cannot all be zero")
    return numerator / denominator
