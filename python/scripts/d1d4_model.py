"""Shared helpers for the D1 / D4 regime checks.

The scripts in this small suite use the same proxy definitions:

- D1: ionization-based attraction proxy already used in the D1/D2 work,
- D4: Fermi pressure and a comparable per-electron balance proxy,
- density scaling: the raw pressure should follow n_e^(5/3).
"""
from __future__ import annotations

import math


R_H_EV = 13.6
HBAR = 1.054571817e-34
M_E = 9.1093837015e-31
E_CHARGE = 1.602176634e-19

FERMI_PRESSURE_FACTOR = ((3.0 * math.pi**2) ** (2.0 / 3.0) / 5.0) * (HBAR**2 / M_E)
FERMI_BALANCE_FACTOR = FERMI_PRESSURE_FACTOR / E_CHARGE


def d1_proxy(ionization_ev: float, principal_n: float) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def fermi_pressure_pa(electron_density_m3: float) -> float:
    return FERMI_PRESSURE_FACTOR * (electron_density_m3 ** (5.0 / 3.0))


def fermi_balance_ev(electron_density_m3: float) -> float:
    return FERMI_BALANCE_FACTOR * (electron_density_m3 ** (2.0 / 3.0))


def density_for_balance(d1_value: float) -> float:
    return (d1_value / FERMI_BALANCE_FACTOR) ** (3.0 / 2.0)


def density_ratio_expected(previous_density: float, next_density: float) -> float:
    return (next_density / previous_density) ** (5.0 / 3.0)


def close_enough(actual: float, expected: float, *, rel_tol: float = 1e-6, abs_tol: float = 1e-9) -> bool:
    return math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol)
