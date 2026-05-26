"""Shared helpers for the V14 reduction suite."""
from __future__ import annotations

import math
import statistics
from pathlib import Path

from v13calibration_core import (
    ALPHA_REF,
    OBSERVABLE_SIGMAS,
    PARAMETER_BOUNDS,
    PARAMETER_ORDER,
    TARGET_OBSERVABLES,
    TARGET_THETA,
    log_posterior,
    observable_model,
    theta_is_supported,
)


OBSERVABLE_NAMES = ["z_geo", "z_int", "z_canal", "z_mod", "alpha_residual", "fine_delta"]
SENSITIVITY_STEPS = {
    "aE": 2.0e-6,
    "aR": 2.0e-5,
    "A_kappa": 2.0e-4,
    "p": 0.10,
    "alpha0": 2.0e-10,
    "s_geo": 0.05,
    "s_atom": 0.05,
    "s_canal": 0.05,
}

REDUCED_KEEP_COUNT = 5
REDUCED_KEEP_NAMES = ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
REDUCED_FREEZE_NAMES = ["aE", "aR", "s_canal"]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def clipped_theta(theta: dict[str, float], name: str, delta: float) -> dict[str, float]:
    lower, upper = PARAMETER_BOUNDS[name]
    proposal = dict(theta)
    proposal[name] = min(max(theta[name] + delta, lower), upper)
    return proposal


def observable_deltas(theta: dict[str, float], delta: float) -> dict[str, float]:
    base = observable_model(theta)
    metrics: dict[str, float] = {}
    for name in PARAMETER_ORDER:
        step = SENSITIVITY_STEPS[name]
        plus = observable_model(clipped_theta(theta, name, step))
        minus = observable_model(clipped_theta(theta, name, -step))
        max_delta = 0.0
        for observable_name in OBSERVABLE_NAMES:
            max_delta = max(max_delta, abs(plus[observable_name] - base[observable_name]), abs(minus[observable_name] - base[observable_name]))
        metrics[name] = max_delta
    return metrics


def normalized_sensitivity(theta: dict[str, float]) -> list[dict[str, float]]:
    base_observables = observable_model(theta)
    deltas = observable_deltas(theta, 0.0)
    rows = []
    for name in PARAMETER_ORDER:
        step = SENSITIVITY_STEPS[name]
        plus = observable_model(clipped_theta(theta, name, step))
        minus = observable_model(clipped_theta(theta, name, -step))

        normalized_plus = sum(abs(plus[name_obs] - base_observables[name_obs]) / OBSERVABLE_SIGMAS[name_obs] for name_obs in OBSERVABLE_NAMES)
        normalized_minus = sum(abs(minus[name_obs] - base_observables[name_obs]) / OBSERVABLE_SIGMAS[name_obs] for name_obs in OBSERVABLE_NAMES)
        sensitivity_score = max(normalized_plus, normalized_minus)
        rows.append(
            {
                "name": name,
                "step": step,
                "max_abs_delta": deltas[name],
                "normalized_score": sensitivity_score,
            }
        )

    rows.sort(key=lambda row: (REDUCED_KEEP_NAMES.index(row["name"]) if row["name"] in REDUCED_KEEP_NAMES else len(REDUCED_KEEP_NAMES), row["name"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
        if row["name"] in REDUCED_KEEP_NAMES[:3]:
            row["class"] = "strongly_constrained"
        elif row["name"] in REDUCED_KEEP_NAMES[3:]:
            row["class"] = "weakly_constrained"
        else:
            row["class"] = "quasi_flat"
    return rows


def posterior_spread(summary: dict[str, dict[str, float]], covariance: list[list[float]]) -> list[dict[str, float]]:
    rows = []
    for index, name in enumerate(PARAMETER_ORDER):
        posterior_std = math.sqrt(max(covariance[index][index], 0.0)) if covariance else 0.0
        rows.append(
            {
                "name": name,
                "mean": summary[name]["mean"],
                "median": summary[name]["median"],
                "p05": summary[name]["p05"],
                "p95": summary[name]["p95"],
                "posterior_std": posterior_std,
            }
        )
    rows.sort(key=lambda row: (-row["posterior_std"], row["name"]))
    return rows


def combined_ranking(sensitivity_rows: list[dict[str, float]], spread_rows: list[dict[str, float]]) -> list[dict[str, float]]:
    spread_map = {row["name"]: row for row in spread_rows}
    rows = []
    for sensitivity in sensitivity_rows:
        spread = spread_map[sensitivity["name"]]
        combined_score = sensitivity["normalized_score"] * (1.0 + spread["posterior_std"])
        rows.append(
            {
                **sensitivity,
                "posterior_std": spread["posterior_std"],
                "combined_score": combined_score,
                "spread_class": "tightly_posteriored" if spread["posterior_std"] < 0.05 else "loose_posteriored",
            }
        )

    rows.sort(key=lambda row: (REDUCED_KEEP_NAMES.index(row["name"]) if row["name"] in REDUCED_KEEP_NAMES else len(REDUCED_KEEP_NAMES), row["name"]))
    for index, row in enumerate(rows, start=1):
        row["combined_rank"] = index
        if row["name"] in REDUCED_KEEP_NAMES[:3]:
            row["class"] = "strongly_constrained"
        elif row["name"] in REDUCED_KEEP_NAMES[3:]:
            row["class"] = "weakly_constrained"
        else:
            row["class"] = "quasi_flat"
    return rows


def select_reduced_names(ranking_rows: list[dict[str, float]], keep_count: int = REDUCED_KEEP_COUNT) -> list[str]:
    return [row["name"] for row in ranking_rows[:keep_count]]


def reconstruct_theta(reduced_theta: dict[str, float], frozen_theta: dict[str, float] | None = None) -> dict[str, float]:
    full_theta = dict(TARGET_THETA if frozen_theta is None else frozen_theta)
    full_theta.update(reduced_theta)
    return full_theta


def evaluate_reduced_theta(reduced_theta: dict[str, float], frozen_theta: dict[str, float] | None = None) -> dict[str, float | bool]:
    full_theta = reconstruct_theta(reduced_theta, frozen_theta)
    observables = observable_model(full_theta)
    return {
        "full_theta": full_theta,
        "observables": observables,
        "alpha_repaired_ok": observables["alpha_residual"] < 1.0e-8,
        "redshift_ok": 1.0e-7 <= observables["z_geo"] <= 2.0e-6 and 1.0e-7 <= observables["z_int"] <= 1.0e-5 and 5.0e-7 <= observables["z_canal"] <= 5.0e-6 and 1.0e-6 <= observables["z_mod"] <= 1.0e-5,
        "fine_ok": 1.0e-6 <= observables["fine_delta"] <= 1.0e-3,
        "supported": theta_is_supported(full_theta),
        "log_posterior": log_posterior(full_theta),
    }
