"""Integrated torsion invariant."""
from __future__ import annotations

from math import sqrt
from typing import Sequence


def omega_torsion(points: Sequence[Sequence[float]]) -> float:
    if len(points) < 4:
        raise ValueError("omega_torsion requires at least 4 points")

    total = 0.0
    for index in range(1, len(points) - 2):
        p0 = points[index - 1]
        p1 = points[index]
        p2 = points[index + 1]
        p3 = points[index + 2]

        v1 = [p1[i] - p0[i] for i in range(3)]
        v2 = [p2[i] - p1[i] for i in range(3)]
        v3 = [p3[i] - p2[i] for i in range(3)]

        cross = [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0],
        ]
        numerator = cross[0] * v3[0] + cross[1] * v3[1] + cross[2] * v3[2]
        denominator = sqrt(sum(value * value for value in cross)) + 1.0e-12
        total += numerator / denominator

    return total
