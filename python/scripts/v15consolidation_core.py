"""Shared helpers for the V15 consolidation suite."""
from __future__ import annotations

import math
from pathlib import Path

from v13calibration_core import OBSERVABLE_SIGMAS, PARAMETER_BOUNDS, TARGET_THETA, observable_model, theta_is_supported
from v14reduction_core import REDUCED_FREEZE_NAMES, REDUCED_KEEP_NAMES, evaluate_reduced_theta, reconstruct_theta, workspace_root


PERTURBATION_LEVELS = [0.01, 0.05, 0.10]
ALPHA_NOISE_SCALE = OBSERVABLE_SIGMAS["alpha_residual"]
FINAL_LOCKED_NAMES = list(REDUCED_KEEP_NAMES)
FINAL_FROZEN_NAMES = list(REDUCED_FREEZE_NAMES)


def final_locked_theta() -> dict[str, float]:
    return {name: TARGET_THETA[name] for name in FINAL_LOCKED_NAMES}


def final_frozen_theta() -> dict[str, float]:
    return {name: TARGET_THETA[name] for name in FINAL_FROZEN_NAMES}


def consolidated_theta() -> dict[str, float]:
    return reconstruct_theta(final_locked_theta(), TARGET_THETA)


def perturb_reduced_theta(theta: dict[str, float], name: str, level: float, sign: int) -> dict[str, float]:
    proposal = dict(theta)
    if name == "alpha0":
        delta = sign * level * ALPHA_NOISE_SCALE
    else:
        delta = sign * level * theta[name]
    lower, upper = PARAMETER_BOUNDS[name]
    proposal[name] = min(max(theta[name] + delta, lower), upper)
    return proposal


def evaluate_stability_case(theta: dict[str, float], name: str, level: float) -> dict[str, object]:
    plus_theta = perturb_reduced_theta(theta, name, level, +1)
    minus_theta = perturb_reduced_theta(theta, name, level, -1)
    plus = evaluate_reduced_theta(plus_theta)
    minus = evaluate_reduced_theta(minus_theta)
    plus_observables = plus["observables"]
    minus_observables = minus["observables"]
    return {
        "name": name,
        "level": level,
        "plus_supported": plus["supported"],
        "minus_supported": minus["supported"],
        "plus_observables": plus_observables,
        "minus_observables": minus_observables,
        "plus_alpha_residual": plus_observables["alpha_residual"],
        "minus_alpha_residual": minus_observables["alpha_residual"],
        "base_supported": evaluate_reduced_theta(theta)["supported"],
    }


def observable_trend(values: list[float], direction: str) -> bool:
    pairs = list(zip(values, values[1:]))
    if direction == "increasing":
        return all(right > left for left, right in pairs)
    if direction == "decreasing":
        return all(right < left for left, right in pairs)
    if direction == "symmetric":
        midpoint = len(values) // 2
        return all(math.isclose(values[left], values[-left - 1], rel_tol=0.0, abs_tol=1.0e-12) for left in range(midpoint))
    raise ValueError(f"Unknown direction: {direction}")


def evaluate_robustness_case(theta: dict[str, float], name: str) -> dict[str, object]:
    levels = [-level for level in reversed(PERTURBATION_LEVELS)] + [0.0] + PERTURBATION_LEVELS
    observables = [evaluate_reduced_theta(perturb_reduced_theta(theta, name, abs(level), 1 if level >= 0 else -1))["observables"] for level in levels]
    values_by_name = {
        observable_name: [row[observable_name] for row in observables]
        for observable_name in ["z_geo", "z_int", "z_canal", "z_mod", "alpha_residual", "fine_delta"]
    }

    if name == "alpha0":
        checks = {
            "alpha_residual_symmetric": observable_trend(values_by_name["alpha_residual"], "symmetric")
            and observable_trend(values_by_name["alpha_residual"][len(values_by_name["alpha_residual"]) // 2 :], "increasing"),
        }
    elif name == "s_geo":
        checks = {
            "z_geo_increasing": observable_trend(values_by_name["z_geo"], "increasing"),
            "z_mod_increasing": observable_trend(values_by_name["z_mod"], "increasing"),
        }
    elif name == "s_atom":
        checks = {
            "z_int_increasing": observable_trend(values_by_name["z_int"], "increasing"),
            "z_mod_increasing": observable_trend(values_by_name["z_mod"], "increasing"),
        }
    elif name == "A_kappa":
        checks = {
            "z_canal_increasing": observable_trend(values_by_name["z_canal"], "increasing"),
            "fine_delta_increasing": observable_trend(values_by_name["fine_delta"], "increasing"),
        }
    elif name == "p":
        checks = {
            "z_mod_increasing": observable_trend(values_by_name["z_mod"], "increasing"),
            "fine_delta_decreasing": observable_trend(values_by_name["fine_delta"], "decreasing"),
        }
    else:
        raise ValueError(f"Unexpected reduced parameter: {name}")

    return {
        "name": name,
        "levels": levels,
        "values_by_name": values_by_name,
        "checks": checks,
        "supported": all(checks.values()),
    }


def evaluate_locked_theta(theta: dict[str, float]) -> dict[str, object]:
    evaluation = evaluate_reduced_theta(theta)
    return {
        "locked_names": list(FINAL_LOCKED_NAMES),
        "frozen_names": list(FINAL_FROZEN_NAMES),
        "reduced_theta": {name: theta[name] for name in FINAL_LOCKED_NAMES},
        "full_theta": evaluation["full_theta"],
        "observables": evaluation["observables"],
        "supported": evaluation["supported"],
        "alpha_repaired_ok": evaluation["alpha_repaired_ok"],
        "redshift_ok": evaluation["redshift_ok"],
        "fine_ok": evaluation["fine_ok"],
    }