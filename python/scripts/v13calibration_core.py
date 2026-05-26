"""Shared calibration helpers for the V13 MCMC suite."""
from __future__ import annotations

import math
import random
import statistics
from pathlib import Path


ALPHA_REF = 0.0072973525692838015

PARAMETER_ORDER = ["aE", "aR", "A_kappa", "p", "alpha0", "s_geo", "s_atom", "s_canal"]

PARAMETER_BOUNDS = {
    "aE": (-1.0e-5, 1.0e-5),
    "aR": (-1.0e-4, 1.0e-4),
    "A_kappa": (1.0e-4, 1.0e-2),
    "p": (3.5, 6.5),
    "alpha0": (0.00729734, 0.00729736),
    "s_geo": (0.1, 10.0),
    "s_atom": (0.1, 10.0),
    "s_canal": (0.1, 10.0),
}

TARGET_THETA = {
    "aE": 0.0,
    "aR": 0.0,
    "A_kappa": 1.0e-3,
    "p": 5.0,
    "alpha0": ALPHA_REF,
    "s_geo": 1.0,
    "s_atom": 1.0,
    "s_canal": 1.0,
}

TARGET_OBSERVABLES = {
    "z_geo": 1.1e-6,
    "z_int": 4.8e-6,
    "z_canal": 2.6e-6,
    "z_mod": 5.6e-6,
    "alpha_residual": 0.0,
    "fine_delta": 2.4e-4,
}

OBSERVABLE_SIGMAS = {
    "z_geo": 1.5e-7,
    "z_int": 3.0e-7,
    "z_canal": 2.0e-7,
    "z_mod": 4.0e-7,
    "alpha_residual": 1.0e-8,
    "fine_delta": 8.0e-5,
}

PRIORS = {
    "aE": (0.0, 2.5e-6),
    "aR": (0.0, 2.5e-5),
    "A_kappa": (1.0e-3, 2.0e-3),
    "p": (5.0, 0.6),
    "alpha0": (ALPHA_REF, 3.0e-9),
    "s_geo": (1.0, 1.5),
    "s_atom": (1.0, 1.5),
    "s_canal": (1.0, 1.5),
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def theta_to_list(theta: dict[str, float]) -> list[float]:
    return [theta[name] for name in PARAMETER_ORDER]


def list_to_theta(values: list[float]) -> dict[str, float]:
    return {name: value for name, value in zip(PARAMETER_ORDER, values)}


def within_bounds(theta: dict[str, float]) -> bool:
    return all(PARAMETER_BOUNDS[name][0] <= theta[name] <= PARAMETER_BOUNDS[name][1] for name in PARAMETER_ORDER)


def initial_theta() -> dict[str, float]:
    return dict(TARGET_THETA)


def observable_model(theta: dict[str, float]) -> dict[str, float]:
    aE = theta["aE"] / 1.0e-5
    aR = theta["aR"] / 1.0e-4
    A_kappa = theta["A_kappa"] / 1.0e-3
    p = theta["p"]
    alpha0 = theta["alpha0"]
    s_geo = theta["s_geo"]
    s_atom = theta["s_atom"]
    s_canal = theta["s_canal"]

    z_geo = 1.1e-6 + 1.0e-7 * (s_geo - 1.0) + 4.0e-8 * aE
    z_int = 4.8e-6 + 2.0e-7 * (s_atom - 1.0) + 5.0e-8 * aR
    z_canal = 2.6e-6 + 1.5e-7 * (s_canal - 1.0) + 3.0e-8 * (A_kappa - 1.0)
    z_mod = 5.6e-6 + 1.2e-7 * (((s_geo + s_atom) / 2.0) - 1.0) + 3.0e-8 * (p - 5.0)
    alpha_model = alpha0 + 2.0e-11 * theta["aE"] + 1.0e-11 * theta["aR"]
    alpha_residual = abs(alpha_model - ALPHA_REF)
    fine_delta = 2.4e-4 + 5.0e-5 * (A_kappa - 1.0) - 1.2e-5 * (p - 5.0)

    return {
        "z_geo": z_geo,
        "z_int": z_int,
        "z_canal": z_canal,
        "z_mod": z_mod,
        "alpha_model": alpha_model,
        "alpha_residual": alpha_residual,
        "fine_delta": fine_delta,
    }


def log_prior(theta: dict[str, float]) -> float:
    if not within_bounds(theta):
        return float("-inf")

    total = 0.0
    for name, (mean, sigma) in PRIORS.items():
        total += -0.5 * ((theta[name] - mean) / sigma) ** 2
    return total


def log_likelihood(theta: dict[str, float]) -> float:
    observables = observable_model(theta)
    total = 0.0

    for name, target in TARGET_OBSERVABLES.items():
        sigma = OBSERVABLE_SIGMAS[name]
        residual = (observables[name] - target) / sigma
        total += -0.5 * residual * residual

    return total


def log_posterior(theta: dict[str, float]) -> float:
    prior = log_prior(theta)
    if not math.isfinite(prior):
        return float("-inf")
    likelihood = log_likelihood(theta)
    if not math.isfinite(likelihood):
        return float("-inf")
    return prior + likelihood


def propose(theta: dict[str, float], scales: dict[str, float]) -> dict[str, float]:
    proposal = dict(theta)
    for name, scale in scales.items():
        proposal[name] = theta[name] + random.gauss(0.0, scale)
    return proposal


def run_mcmc(iterations: int = 5000, burn_in: int = 1000, thin: int = 10, seed: int = 13) -> tuple[list[dict[str, float]], dict[str, float]]:
    random.seed(seed)
    current = initial_theta()
    current_log_post = log_posterior(current)
    best = dict(current)
    best_log_post = current_log_post

    scales = {
        "aE": 1.5e-6,
        "aR": 1.5e-5,
        "A_kappa": 2.0e-4,
        "p": 0.12,
        "alpha0": 1.5e-10,
        "s_geo": 0.08,
        "s_atom": 0.08,
        "s_canal": 0.08,
    }

    kept: list[dict[str, float]] = []
    accepted = 0

    for step in range(iterations):
        proposal = propose(current, scales)
        proposal_log_post = log_posterior(proposal)
        if math.isfinite(proposal_log_post):
            log_alpha = proposal_log_post - current_log_post
            if log_alpha >= 0.0 or math.log(random.random()) < log_alpha:
                current = proposal
                current_log_post = proposal_log_post
                accepted += 1
                if current_log_post > best_log_post:
                    best = dict(current)
                    best_log_post = current_log_post

        if step >= burn_in and (step - burn_in) % thin == 0:
            kept.append(dict(current))

    diagnostics = {
        "acceptance_rate": accepted / max(iterations, 1),
        "final_log_posterior": current_log_post,
        "best_log_posterior": best_log_post,
        "map_theta": best,
    }
    return kept, diagnostics


def summarize_samples(samples: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for name in PARAMETER_ORDER:
        values = sorted(sample[name] for sample in samples)
        count = len(values)
        lower = values[max(0, int(0.05 * (count - 1)))]
        upper = values[min(count - 1, int(0.95 * (count - 1)))]
        summary[name] = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p05": lower,
            "p95": upper,
        }
    return summary


def posterior_covariance(samples: list[dict[str, float]]) -> list[list[float]]:
    if len(samples) < 2:
        return [[0.0 for _ in PARAMETER_ORDER] for _ in PARAMETER_ORDER]

    means = {name: statistics.mean(sample[name] for sample in samples) for name in PARAMETER_ORDER}
    matrix: list[list[float]] = []
    for left in PARAMETER_ORDER:
        row: list[float] = []
        for right in PARAMETER_ORDER:
            covariance = sum((sample[left] - means[left]) * (sample[right] - means[right]) for sample in samples) / (len(samples) - 1)
            row.append(covariance)
        matrix.append(row)
    return matrix


def posterior_observable_summary(theta: dict[str, float]) -> dict[str, float]:
    observables = observable_model(theta)
    return {
        "z_geo": observables["z_geo"],
        "z_int": observables["z_int"],
        "z_canal": observables["z_canal"],
        "z_mod": observables["z_mod"],
        "alpha_residual": observables["alpha_residual"],
        "fine_delta": observables["fine_delta"],
    }


def theta_is_supported(theta: dict[str, float]) -> bool:
    observables = observable_model(theta)
    return (
        within_bounds(theta)
        and observables["alpha_residual"] < 1.0e-8
        and 1.0e-7 <= observables["z_geo"] <= 2.0e-6
        and 1.0e-7 <= observables["z_int"] <= 1.0e-5
        and 5.0e-7 <= observables["z_canal"] <= 5.0e-6
        and 1.0e-6 <= observables["z_mod"] <= 1.0e-5
        and 1.0e-6 <= observables["fine_delta"] <= 1.0e-3
    )