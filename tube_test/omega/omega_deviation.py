"""Quadratic geometric deviation invariant."""
from __future__ import annotations

from math import sqrt
from typing import Sequence


def omega_deviation(points: Sequence[Sequence[float]]) -> float:
    if len(points) < 2:
        raise ValueError("omega_deviation requires at least 2 points")

    start = points[0]
    end = points[-1]
    direction = [end[i] - start[i] for i in range(3)]
    length = sqrt(sum(value * value for value in direction))
    if length == 0.0:
        return 0.0

    total = 0.0
    for point in points:
        ratio = sum((point[i] - start[i]) * direction[i] for i in range(3)) / (length * length)
        projected = [start[i] + ratio * direction[i] for i in range(3)]
        total += sum((point[i] - projected[i]) ** 2 for i in range(3))

    return total / len(points)
