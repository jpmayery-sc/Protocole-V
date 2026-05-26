"""Normalized winding invariant."""
from __future__ import annotations

from typing import Sequence


def omega_winding(theta_samples: Sequence[float]) -> float:
    if len(theta_samples) < 2:
        raise ValueError("omega_winding requires at least 2 samples")
    return (theta_samples[-1] - theta_samples[0]) / (2.0 * 3.141592653589793)
