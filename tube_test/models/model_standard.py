"""Standard reference model for numeric comparisons."""
from __future__ import annotations

from typing import Sequence


def predict_standard(observable: str, baseline: float, samples: Sequence[float]) -> list[float]:
    del observable
    return [baseline for _ in samples]


def residuals(observed: Sequence[float], predicted: Sequence[float]) -> list[float]:
    return [obs - pred for obs, pred in zip(observed, predicted)]
