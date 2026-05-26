"""Estimate the robust MIN_NEUTRON region with a lightweight MCMC.

The sampler uses the existing sweep summary as an empirical target and fits a
simple basin model to the absolute epsilon residuals. The goal is not to prove
the theory, but to localize the stable region and quantify its uncertainty.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import csv
import json
import math
import random
import statistics
import time
from pathlib import Path


@dataclass(frozen=True)
class SweepPoint:
    n_value: int
    min_neutron: int
    score: float


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def latest_sweep_csv(results_dir: Path) -> Path:
    candidates = sorted(results_dir.glob("sweep_summary_*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No sweep_summary_*.csv file found in {results_dir}")
    return candidates[0]


def load_points(csv_path: Path) -> list[SweepPoint]:
    points: list[SweepPoint] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            points.append(
                SweepPoint(
                    n_value=int(row["N"]),
                    min_neutron=int(row["MIN_NEUTRON"]),
                    score=abs(float(row["eps"])),
                )
            )

    if not points:
        raise ValueError(f"No data loaded from {csv_path}")

    return points


def initial_guess(points: list[SweepPoint]) -> dict[str, float]:
    grouped: dict[int, list[SweepPoint]] = {}
    for point in points:
        grouped.setdefault(point.n_value, []).append(point)

    best_by_group = [min(group, key=lambda item: item.score) for group in grouped.values()]
    mu = statistics.mean(point.min_neutron for point in best_by_group)
    best_score = min(point.score for point in points)
    offsets = {n_value: max(min(point.score for point in group) - 0.01, 1.0e-6) for n_value, group in grouped.items()}

    return {
        "mu": mu,
        "log_a": math.log(1.0e-3),
        "log_sigma": math.log(max(best_score, 1.0e-3)),
        "offset_60": offsets.get(60, 0.01),
        "offset_100": offsets.get(100, 0.01),
        "offset_200": offsets.get(200, 0.01),
    }


def log_prior(params: dict[str, float]) -> float:
    mu = params["mu"]
    log_a = params["log_a"]
    log_sigma = params["log_sigma"]
    offset_60 = params["offset_60"]
    offset_100 = params["offset_100"]
    offset_200 = params["offset_200"]

    if not (15.0 <= mu <= 40.0):
        return float("-inf")
    if offset_60 <= 0.0 or offset_100 <= 0.0 or offset_200 <= 0.0:
        return float("-inf")

    prior = 0.0
    prior += -0.5 * ((log_a - math.log(1.0e-3)) / 1.5) ** 2
    prior += -0.5 * ((log_sigma - math.log(0.05)) / 1.2) ** 2
    prior += -0.5 * ((offset_60 - 0.03) / 0.05) ** 2
    prior += -0.5 * ((offset_100 - 0.08) / 0.07) ** 2
    prior += -0.5 * ((offset_200 - 0.10) / 0.08) ** 2
    return prior


def log_likelihood(points: list[SweepPoint], params: dict[str, float]) -> float:
    mu = params["mu"]
    a = math.exp(params["log_a"])
    sigma = math.exp(params["log_sigma"])

    if sigma <= 0.0:
        return float("-inf")

    offsets = {
        60: params["offset_60"],
        100: params["offset_100"],
        200: params["offset_200"],
    }

    inv_two_sigma_sq = 0.5 / (sigma * sigma)
    normalizer = math.log(sigma) + 0.5 * math.log(2.0 * math.pi)
    total = 0.0

    for point in points:
        offset = offsets.get(point.n_value)
        if offset is None:
            return float("-inf")
        prediction = offset + a * (point.min_neutron - mu) ** 2
        residual = point.score - prediction
        total += -(residual * residual) * inv_two_sigma_sq - normalizer

    return total


def log_posterior(points: list[SweepPoint], params: dict[str, float]) -> float:
    prior = log_prior(params)
    if not math.isfinite(prior):
        return float("-inf")
    likelihood = log_likelihood(points, params)
    if not math.isfinite(likelihood):
        return float("-inf")
    return prior + likelihood


def propose(current: dict[str, float], scales: dict[str, float]) -> dict[str, float]:
    proposal = dict(current)
    for key, scale in scales.items():
        proposal[key] = current[key] + random.gauss(0.0, scale)
    return proposal


def run_mcmc(points: list[SweepPoint], iterations: int, burn_in: int, thin: int, seed: int) -> tuple[list[dict[str, float]], dict[str, float]]:
    random.seed(seed)
    current = initial_guess(points)
    current_log_post = log_posterior(points, current)

    scales = {
        "mu": 0.20,
        "log_a": 0.08,
        "log_sigma": 0.06,
        "offset_60": 0.003,
        "offset_100": 0.003,
        "offset_200": 0.003,
    }

    samples: list[dict[str, float]] = []
    accepted = 0

    for step in range(iterations):
        proposal = propose(current, scales)
        proposal_log_post = log_posterior(points, proposal)

        if math.isfinite(proposal_log_post):
            log_alpha = proposal_log_post - current_log_post
            if log_alpha >= 0.0 or math.log(random.random()) < log_alpha:
                current = proposal
                current_log_post = proposal_log_post
                accepted += 1

        if step >= burn_in and (step - burn_in) % thin == 0:
            samples.append(dict(current))

    diagnostics = {
        "acceptance_rate": accepted / max(iterations, 1),
        "final_log_posterior": current_log_post,
    }
    return samples, diagnostics


def summarize_samples(samples: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for key in ["mu", "log_a", "log_sigma", "offset_60", "offset_100", "offset_200"]:
        values = sorted(sample[key] for sample in samples)
        count = len(values)
        lower = values[max(0, int(0.05 * (count - 1)))]
        upper = values[min(count - 1, int(0.95 * (count - 1)))]
        summary[key] = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "p05": lower,
            "p95": upper,
        }
    return summary


def posterior_window_mass(samples: list[dict[str, float]], low: float, high: float) -> float:
    if not samples:
        return float("nan")
    count = sum(1 for sample in samples if low <= sample["mu"] <= high)
    return count / len(samples)


def posterior_predictive_summary(points: list[SweepPoint], samples: list[dict[str, float]]) -> dict[str, float | dict[int, float]]:
    grouped_scores: dict[int, list[float]] = {}
    for point in points:
        grouped_scores.setdefault(point.n_value, []).append(point.score)

    null_predictions = {
        n_value: statistics.mean(scores)
        for n_value, scores in grouped_scores.items()
    }

    predictive_means: dict[tuple[int, int], list[float]] = {}
    squared_error_sum = 0.0
    null_squared_error_sum = 0.0
    count = 0

    for point in points:
        predictions = []
        for sample in samples:
            offset = sample[f"offset_{point.n_value}"]
            a = math.exp(sample["log_a"])
            mu = sample["mu"]
            predictions.append(offset + a * (point.min_neutron - mu) ** 2)

        predictive_mean = statistics.mean(predictions)
        predictive_means[(point.n_value, point.min_neutron)] = predictions
        squared_error_sum += (point.score - predictive_mean) ** 2
        null_squared_error_sum += (point.score - null_predictions[point.n_value]) ** 2
        count += 1

    return {
        "posterior_predictive_rmse": math.sqrt(squared_error_sum / max(count, 1)),
        "null_rmse": math.sqrt(null_squared_error_sum / max(count, 1)),
        "rmse_margin": math.sqrt(null_squared_error_sum / max(count, 1)) - math.sqrt(squared_error_sum / max(count, 1)),
        "null_predictions": null_predictions,
        "samples_per_point": len(samples),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal MCMC on the MIN_NEUTRON sweep.")
    parser.add_argument("--input", type=Path, help="Path to a sweep_summary_*.csv file")
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--burn-in", type=int, default=5000)
    parser.add_argument("--thin", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    results_dir = project_root() / "results"
    results_dir.mkdir(exist_ok=True)

    csv_path = args.input if args.input is not None else latest_sweep_csv(results_dir)
    points = load_points(csv_path)

    samples, diagnostics = run_mcmc(points, iterations=args.iterations, burn_in=args.burn_in, thin=args.thin, seed=args.seed)
    summary = summarize_samples(samples)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = results_dir / f"mcmc_min_neutron_{timestamp}.json"
    txt_path = results_dir / f"mcmc_min_neutron_{timestamp}.txt"

    payload = {
        "timestamp": timestamp,
        "input_csv": str(csv_path),
        "n_points": len(points),
        "iterations": args.iterations,
        "burn_in": args.burn_in,
        "thin": args.thin,
        "diagnostics": diagnostics,
        "summary": summary,
        "posterior_predictive": posterior_predictive_summary(points, samples),
        "window_mass_32_35": posterior_window_mass(samples, 32.0, 35.0),
        "window_mass_33_35": posterior_window_mass(samples, 33.0, 35.0),
        "samples_kept": len(samples),
    }

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("MCMC MIN_NEUTRON\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Input: {csv_path}\n")
        handle.write(f"Points: {len(points)}\n")
        handle.write(f"Iterations: {args.iterations}\n")
        handle.write(f"Burn-in: {args.burn_in}\n")
        handle.write(f"Thin: {args.thin}\n")
        handle.write(f"Acceptance rate: {diagnostics['acceptance_rate']:.3f}\n")
        handle.write(f"Posterior mass in [32, 35]: {payload['window_mass_32_35']:.3f}\n")
        handle.write(f"Posterior mass in [33, 35]: {payload['window_mass_33_35']:.3f}\n\n")
        handle.write(f"Posterior predictive RMSE: {payload['posterior_predictive']['posterior_predictive_rmse']:.6f}\n")
        handle.write(f"Null RMSE: {payload['posterior_predictive']['null_rmse']:.6f}\n")
        handle.write(f"RMSE margin: {payload['posterior_predictive']['rmse_margin']:.6f}\n\n")
        for key, stats in summary.items():
            handle.write(
                f"{key}: mean={stats['mean']:.6f}, median={stats['median']:.6f}, "
                f"p05={stats['p05']:.6f}, p95={stats['p95']:.6f}\n"
            )

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Acceptance rate: {diagnostics['acceptance_rate']:.3f}")
    print(f"Posterior mass in [32, 35]: {payload['window_mass_32_35']:.3f}")
    print(f"Posterior mass in [33, 35]: {payload['window_mass_33_35']:.3f}")
    print(f"Posterior predictive RMSE: {payload['posterior_predictive']['posterior_predictive_rmse']:.6f}")
    print(f"Null RMSE: {payload['posterior_predictive']['null_rmse']:.6f}")


if __name__ == "__main__":
    main()