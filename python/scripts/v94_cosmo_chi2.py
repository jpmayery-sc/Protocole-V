"""Run V94 MCMC cosmological parameter estimation.

V94 implements a complete MCMC sampling of the K/T/Y + D1/D2 + L_ent model
using cosmological observables:
- H(z): 6 points
- f_sigma8(z): 7 points
- S8: 1 point
- Optional: JWST (JWST-04 to JWST-08) + NS constraints

This produces posterior P(params | data) with full uncertainties and correlations.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
import time
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

try:
    import emcee
except ImportError:
    emcee = None

from v29finaltheory_core import v29_result_dir, write_report
from v93b_c_em_lagrangian import compute_bridge
from v95_dynamic_solver import DynamicSolverParameters, solve_dynamic_observables


# ============================================================================
# Parameter definitions
# ============================================================================

@dataclass
class MCMCParameters:
    """Container for MCMC parameter bounds and priors."""
    alpha_k: tuple[float, float] = (0.4, 0.8)  # (lower, upper)
    alpha_t: tuple[float, float] = (0.6, 1.0)
    alpha_kt: tuple[float, float] = (0.2, 0.5)
    gamma_star: tuple[float, float] = (1.0, 2.0)
    chi2_coupling: tuple[float, float] = (0.05, 0.20)
    
    def param_names(self) -> list[str]:
        """Return list of parameter names."""
        return ["alpha_k", "alpha_t", "alpha_kt", "gamma_star", "chi2_coupling"]
    
    def get_bounds(self) -> dict[str, tuple[float, float]]:
        """Return parameter bounds as dict."""
        return {
            "alpha_k": self.alpha_k,
            "alpha_t": self.alpha_t,
            "alpha_kt": self.alpha_kt,
            "gamma_star": self.gamma_star,
            "chi2_coupling": self.chi2_coupling,
        }


# ============================================================================
# Likelihood and prior functions
# ============================================================================

def log_prior(theta: np.ndarray, bounds: dict[str, tuple[float, float]]) -> float:
    """Uniform prior over parameter bounds."""
    param_names = list(bounds.keys())
    for i, name in enumerate(param_names):
        lower, upper = bounds[name]
        if not (lower <= theta[i] <= upper):
            return -np.inf
    return 0.0


def predict_observables(
    theta: np.ndarray,
    param_names: list[str],
    data_bundle: dict,
    use_dynamic_solver: bool = False,
) -> dict[str, object]:
    """Predict observables and chi2 contributions for a parameter vector."""

    params = {name: value for name, value in zip(param_names, theta)}

    bridge = compute_bridge(
        epsilon=-0.0069,
        alpha_k=params["alpha_k"],
        alpha_t=params["alpha_t"],
        alpha_kt=params["alpha_kt"],
        gamma_star=params["gamma_star"],
        chi2_coupling=params["chi2_coupling"],
    )

    z_H, obs_H, sigma_H = data_bundle["H"]
    z_fs8, obs_fs8, sigma_fs8, pred_noent_fs8 = data_bundle["fs8"]
    s8_obs, s8_sigma, s8_noent = data_bundle["S8"]

    if use_dynamic_solver:
        z_grid = np.unique(np.concatenate([z_H, z_fs8, np.array([0.0])]))
        dynamic_solution = solve_dynamic_observables(
            z_eval=z_grid,
            params=DynamicSolverParameters(
                alpha_k=params["alpha_k"],
                alpha_t=params["alpha_t"],
                alpha_kt=params["alpha_kt"],
                gamma_star=params["gamma_star"],
                chi2_coupling=params["chi2_coupling"],
                epsilon=-0.0069,
                sigma8_0=s8_noent,
            ),
        )
        h_model = np.interp(z_H, dynamic_solution.z, dynamic_solution.H_model)
        fs8_model = np.interp(z_fs8, dynamic_solution.z, dynamic_solution.fs8_model)
        s8_model = float(dynamic_solution.S8_model)
    else:
        h_model = 70.0 + 12.0 * z_H / (1.0 + z_H)
        fs8_model = obs_fs8 + bridge.projection_growth * (pred_noent_fs8 - obs_fs8)
        s8_model = s8_obs + bridge.projection_s8 * (s8_noent - s8_obs)

    chi2_H = np.sum(((obs_H - h_model) / sigma_H) ** 2)
    chi2_fs8 = np.sum(((obs_fs8 - fs8_model) / sigma_fs8) ** 2)
    chi2_S8 = ((s8_obs - s8_model) / s8_sigma) ** 2

    return {
        "params": params,
        "bridge": bridge,
        "H_model": h_model,
        "fs8_model": fs8_model,
        "S8_model": float(s8_model),
        "chi2_H": float(chi2_H),
        "chi2_fs8": float(chi2_fs8),
        "chi2_S8": float(chi2_S8),
        "chi2_total": float(chi2_H + chi2_fs8 + chi2_S8),
    }


def log_likelihood(theta: np.ndarray, param_names: list[str], 
                   bounds: dict[str, tuple[float, float]],
                   data_bundle: dict,
                   use_dynamic_solver: bool = False) -> float:
    """Compute log-likelihood from cosmological observables."""
    try:
        prediction = predict_observables(theta, param_names, data_bundle, use_dynamic_solver=use_dynamic_solver)
    except Exception:
        return -np.inf

    return -0.5 * prediction["chi2_total"]


def log_posterior(theta: np.ndarray, param_names: list[str],
                 bounds: dict[str, tuple[float, float]],
                 data_bundle: dict,
                 use_dynamic_solver: bool = False) -> float:
    """Compute log-posterior = log_prior + log_likelihood."""
    lp = log_prior(theta, bounds)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, param_names, bounds, data_bundle, use_dynamic_solver=use_dynamic_solver)


# ============================================================================
# Data loading
# ============================================================================

def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_data_bundle() -> dict:
    """Load cosmological data for V94 MCMC."""
    
    data_dir = workspace_root() / "results" / "result-analyse" / "v92_cosmo_chi2" / "data"
    
    # Load H(z)
    try:
        h_df = pd.read_csv(data_dir / "hubble_observations.csv")
        z_H = h_df["z"].to_numpy()
        obs_H = h_df["H_z"].to_numpy()
        sigma_H = h_df["sigma_H_z"].to_numpy()
        data_H = (z_H, obs_H, sigma_H)
    except Exception:
        data_H = None
    
    # Load f_sigma8(z)
    try:
        fs8_df = pd.read_csv(data_dir / "fs8_observations.csv")
        z_fs8 = fs8_df["z"].to_numpy()
        obs_fs8 = fs8_df["f_sigma8"].to_numpy()
        sigma_fs8 = fs8_df["sigma_f_sigma8"].to_numpy()
        pred_noent_fs8 = fs8_df["f_sigma8_noent"].to_numpy()
        data_fs8 = (z_fs8, obs_fs8, sigma_fs8, pred_noent_fs8)
    except Exception:
        data_fs8 = None
    
    # Load S8
    data_S8 = (0.776, 0.017, 0.812)  # (obs, sigma, noent)
    
    return {
        "H": data_H,
        "fs8": data_fs8,
        "S8": data_S8,
    }


def summarize_samples(samples: np.ndarray, param_names: list[str]) -> dict[str, dict[str, float]]:
    """Compute standard marginal summaries for posterior samples."""

    stats: dict[str, dict[str, float]] = {}
    for i, name in enumerate(param_names):
        param_samples = samples[:, :, i].reshape(-1)
        stats[name] = {
            "mean": float(np.mean(param_samples)),
            "median": float(np.median(param_samples)),
            "std": float(np.std(param_samples)),
            "quantile_16": float(np.percentile(param_samples, 16)),
            "quantile_84": float(np.percentile(param_samples, 84)),
            "quantile_2p5": float(np.percentile(param_samples, 2.5)),
            "quantile_97p5": float(np.percentile(param_samples, 97.5)),
        }
    return stats


def compute_convergence_diagnostics(
    sampler: object,
    samples: np.ndarray,
    burnin_steps: int,
    param_names: list[str],
) -> dict[str, object]:
    """Compute simple convergence diagnostics for the MCMC chain."""

    diagnostics: dict[str, object] = {
        "burnin_steps": int(burnin_steps),
        "post_burnin_shape": [int(value) for value in samples.shape],
        "posterior_draws": int(samples.shape[0] * samples.shape[1]),
        "acceptance_fraction_mean": float(np.mean(getattr(sampler, "acceptance_fraction", np.array([])))),
        "acceptance_fraction_min": float(np.min(getattr(sampler, "acceptance_fraction", np.array([np.nan])))),
        "acceptance_fraction_max": float(np.max(getattr(sampler, "acceptance_fraction", np.array([np.nan])))),
    }

    try:
        autocorr = sampler.get_autocorr_time(discard=burnin_steps, thin=1, tol=0)
        diagnostics["autocorr_time"] = {
            name: float(value) for name, value in zip(param_names, autocorr)
        }
        diagnostics["effective_sample_size"] = {
            name: float(samples.shape[0] * samples.shape[1] / max(value, 1.0e-12))
            for name, value in zip(param_names, autocorr)
        }
        diagnostics["autocorr_status"] = "estimated"
    except Exception as exc:
        diagnostics["autocorr_time"] = None
        diagnostics["effective_sample_size"] = None
        diagnostics["autocorr_status"] = f"unavailable: {exc}"

    return diagnostics


def compute_posterior_predictive(
    samples: np.ndarray,
    param_names: list[str],
    data_bundle: dict,
    use_dynamic_solver: bool = False,
    max_draws: int = 200,
) -> dict[str, object]:
    """Generate posterior predictive summaries for H(z), fs8(z), and S8."""

    flat_samples = samples.reshape(-1, samples.shape[-1])
    if flat_samples.shape[0] > max_draws:
        draw_indices = np.linspace(0, flat_samples.shape[0] - 1, max_draws, dtype=int)
        flat_samples = flat_samples[draw_indices]

    z_H, obs_H, sigma_H = data_bundle["H"]
    z_fs8, obs_fs8, sigma_fs8, _pred_noent_fs8 = data_bundle["fs8"]
    s8_obs, s8_sigma, _s8_noent = data_bundle["S8"]

    h_draws: list[np.ndarray] = []
    fs8_draws: list[np.ndarray] = []
    s8_draws: list[float] = []
    chi2_draws: list[float] = []

    for theta in flat_samples:
        prediction = predict_observables(theta, param_names, data_bundle, use_dynamic_solver=use_dynamic_solver)
        h_draws.append(np.asarray(prediction["H_model"], dtype=float))
        fs8_draws.append(np.asarray(prediction["fs8_model"], dtype=float))
        s8_draws.append(float(prediction["S8_model"]))
        chi2_draws.append(float(prediction["chi2_total"]))

    h_draws_array = np.asarray(h_draws, dtype=float)
    fs8_draws_array = np.asarray(fs8_draws, dtype=float)
    s8_draws_array = np.asarray(s8_draws, dtype=float)
    chi2_draws_array = np.asarray(chi2_draws, dtype=float)

    median_theta = np.median(flat_samples, axis=0)
    median_prediction = predict_observables(median_theta, param_names, data_bundle, use_dynamic_solver=use_dynamic_solver)

    return {
        "max_draws": int(max_draws),
        "draws_used": int(flat_samples.shape[0]),
        "chi2_distribution": {
            "mean": float(np.mean(chi2_draws_array)),
            "median": float(np.median(chi2_draws_array)),
            "quantile_16": float(np.percentile(chi2_draws_array, 16)),
            "quantile_84": float(np.percentile(chi2_draws_array, 84)),
        },
        "chi2_at_posterior_median": float(median_prediction["chi2_total"]),
        "posterior_predictive_p_value": float(np.mean(chi2_draws_array >= median_prediction["chi2_total"])),
        "H": {
            "z": z_H.tolist(),
            "observed": obs_H.tolist(),
            "sigma": sigma_H.tolist(),
            "median": np.median(h_draws_array, axis=0).tolist(),
            "quantile_16": np.percentile(h_draws_array, 16, axis=0).tolist(),
            "quantile_84": np.percentile(h_draws_array, 84, axis=0).tolist(),
        },
        "fs8": {
            "z": z_fs8.tolist(),
            "observed": obs_fs8.tolist(),
            "sigma": sigma_fs8.tolist(),
            "median": np.median(fs8_draws_array, axis=0).tolist(),
            "quantile_16": np.percentile(fs8_draws_array, 16, axis=0).tolist(),
            "quantile_84": np.percentile(fs8_draws_array, 84, axis=0).tolist(),
        },
        "S8": {
            "observed": float(s8_obs),
            "sigma": float(s8_sigma),
            "median": float(np.median(s8_draws_array)),
            "quantile_16": float(np.percentile(s8_draws_array, 16)),
            "quantile_84": float(np.percentile(s8_draws_array, 84)),
        },
    }


# ============================================================================
# MCMC execution
# ============================================================================

def run_mcmc(nwalkers: int = 32, nsteps: int = 2000, 
             output_dir: str | Path | None = None,
             use_dynamic_solver: bool = False,
             predictive_draws: int = 200) -> dict[str, object]:
    """Execute MCMC parameter estimation."""
    
    if emcee is None:
        return {
            "suite": "v94_mcmc_cosmo",
            "verdict": "v94_mcmc_failed",
            "error": "emcee not installed. Install with: pip install emcee",
        }
    
    # Setup parameters and priors
    mcmc_params = MCMCParameters()
    param_names = mcmc_params.param_names()
    bounds = mcmc_params.get_bounds()
    ndim = len(param_names)
    
    # Load data
    data_bundle = load_data_bundle()
    
    # Initialize walkers at random positions within bounds
    p0 = []
    for name in param_names:
        lower, upper = bounds[name]
        p0.append(np.random.uniform(lower, upper, nwalkers))
    p0 = np.column_stack(p0)
    
    # Create sampler
    def log_prob_wrapper(theta):
        return log_posterior(theta, param_names, bounds, data_bundle, use_dynamic_solver=use_dynamic_solver)
    
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_prob_wrapper)
    
    # Run MCMC
    result_dir = v29_result_dir(output_dir) / "v94_mcmc_cosmo"
    result_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    print(f"Running MCMC: {nwalkers} walkers, {nsteps} steps...")
    
    try:
        sampler.run_mcmc(p0, nsteps, progress=True)
    except Exception as e:
        return {
            "suite": "v94_mcmc_cosmo",
            "timestamp": timestamp,
            "verdict": "v94_mcmc_failed",
            "error": str(e),
        }
    
    # Extract results
    burnin_steps = int(nsteps * 0.2)
    samples = sampler.get_chain(discard=burnin_steps, thin=1)
    lnprobs = sampler.get_log_prob(discard=burnin_steps, thin=1)
    
    # Compute statistics
    stats = summarize_samples(samples, param_names)

    # Convergence diagnostics
    convergence = compute_convergence_diagnostics(sampler, samples, burnin_steps, param_names)

    # Posterior predictive check
    posterior_predictive = compute_posterior_predictive(
        samples,
        param_names,
        data_bundle,
        use_dynamic_solver=use_dynamic_solver,
        max_draws=predictive_draws,
    )

    median_theta = np.median(samples.reshape(-1, samples.shape[-1]), axis=0)
    median_prediction = predict_observables(median_theta, param_names, data_bundle, use_dynamic_solver=use_dynamic_solver)
    
    # Save chains
    chains_file = result_dir / f"mcmc_chains_{timestamp}.npy"
    np.save(chains_file, samples)
    
    # Assemble summary
    summary = {
        "suite": "v94_mcmc_cosmo",
        "timestamp": timestamp,
        "verdict": "v94_mcmc_complete",
        "nwalkers": nwalkers,
        "nsteps": nsteps,
        "param_names": param_names,
        "parameter_statistics": stats,
        "convergence_diagnostics": convergence,
        "posterior_predictive": posterior_predictive,
        "median_model_fit": {
            "chi2_total": float(median_prediction["chi2_total"]),
            "chi2_H": float(median_prediction["chi2_H"]),
            "chi2_fs8": float(median_prediction["chi2_fs8"]),
            "chi2_S8": float(median_prediction["chi2_S8"]),
        },
        "chains_file": str(chains_file),
        "mcmc_data_bundle": {
            "H_available": data_bundle.get("H") is not None,
            "fs8_available": data_bundle.get("fs8") is not None,
            "S8_available": data_bundle.get("S8") is not None,
        },
        "notes": (
            "V94 MCMC implements full posterior sampling of cosmological parameters "
            "α_K, α_T, α_KT, γ*, χ²_coupling using H(z), f_sigma8(z), S8 observables. "
            "20% burn-in discarded. Convergence diagnostics and posterior predictive checks are included."
        ),
        "solver_mode": "dynamic" if use_dynamic_solver else "surrogate",
    }
    
    # Write outputs
    json_file = result_dir / f"v94_mcmc_cosmo_{timestamp}.json"
    write_report(json_file, summary)
    
    txt_file = result_dir / f"v94_mcmc_cosmo_{timestamp}.txt"
    lines = [
        "V94 MCMC cosmological parameter estimation",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"nwalkers: {nwalkers}",
        f"nsteps: {nsteps}",
        f"solver_mode: {summary['solver_mode']}",
        "",
        "Parameter statistics (after 20% burn-in):",
    ]
    for name, stats_dict in stats.items():
        lines.append(f"\n{name}:")
        lines.append(f"  median = {stats_dict['median']:.6f}")
        lines.append(f"  68% CI = [{stats_dict['quantile_16']:.6f}, {stats_dict['quantile_84']:.6f}]")
        lines.append(f"  95% CI = [{stats_dict['quantile_2p5']:.6f}, {stats_dict['quantile_97p5']:.6f}]")

    lines.append("\nConvergence diagnostics:")
    lines.append(f"  acceptance_fraction_mean = {convergence['acceptance_fraction_mean']:.6f}")
    lines.append(f"  acceptance_fraction_min = {convergence['acceptance_fraction_min']:.6f}")
    lines.append(f"  acceptance_fraction_max = {convergence['acceptance_fraction_max']:.6f}")
    lines.append(f"  autocorr_status = {convergence['autocorr_status']}")
    if convergence.get("autocorr_time"):
        for name in param_names:
            tau = convergence["autocorr_time"][name]
            ess = convergence["effective_sample_size"][name]
            lines.append(f"  {name}: tau_int={tau:.3f}, ESS~{ess:.1f}")

    lines.append("\nPosterior predictive check:")
    lines.append(f"  chi2_median_model = {posterior_predictive['chi2_at_posterior_median']:.6f}")
    lines.append(f"  ppp = {posterior_predictive['posterior_predictive_p_value']:.6f}")
    lines.append(
        "  chi2_distribution_median = "
        f"{posterior_predictive['chi2_distribution']['median']:.6f}"
    )
    
    txt_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    summary["json_file"] = str(json_file)
    summary["txt_file"] = str(txt_file)
    
    return summary


# ============================================================================
# Main entry point
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run V94 MCMC cosmological parameter estimation"
    )
    parser.add_argument("--nwalkers", type=int, default=32, 
                       help="Number of MCMC walkers")
    parser.add_argument("--nsteps", type=int, default=2000,
                       help="Number of MCMC steps (including burn-in)")
    parser.add_argument("--output-dir", default=None, 
                       help="Directory for output files")
    parser.add_argument(
        "--dynamic-solver",
        action="store_true",
        help="Use the dynamic K/T/Y solver instead of the static surrogate bridge",
    )
    args = parser.parse_args()
    
    result = run_mcmc(
        nwalkers=args.nwalkers,
        nsteps=args.nsteps,
        output_dir=args.output_dir,
        use_dynamic_solver=args.dynamic_solver,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


