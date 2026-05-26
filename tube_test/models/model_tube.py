"""Tube-extended model with a single geometric coefficient."""
from __future__ import annotations

from typing import Sequence


def apply_tube_correction(standard_values: Sequence[float], omega_values: Sequence[float], lambda_value: float) -> list[float]:
    return [std + lambda_value * omega for std, omega in zip(standard_values, omega_values)]
