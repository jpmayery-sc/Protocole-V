#!/usr/bin/env python
"""Generate corner plots and convergence diagnostics for V94 MCMC results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import corner

def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_mcmc_results(output_dir: str | Path | None = None) -> tuple[dict, np.ndarray]:
    """Load V94 MCMC JSON results and chains."""
    
    if output_dir is None:
        output_dir = workspace_root() / "results" / "result-analyse"
    else:
        output_dir = Path(output_dir)
    
    result_dir = output_dir / "v94_mcmc_cosmo"
    
    # Find the most recent JSON file
    json_files = sorted(result_dir.glob("v94_mcmc_cosmo_*.json"))
    if not json_files:
        raise FileNotFoundError(f"No V94 MCMC JSON files found in {result_dir}")
    
    latest_json = json_files[-1]
    with open(latest_json) as f:
        result = json.load(f)
    
    # Load chains
    chain_files = sorted(result_dir.glob("mcmc_chains_*.npy"))
    if not chain_files:
        raise FileNotFoundError(f"No MCMC chain files found in {result_dir}")
    
    latest_chains = chain_files[-1]
    chains = np.load(latest_chains)  # shape: (nsteps, nwalkers, ndim) or (nsamples, ndim)
    
    return result, chains


def plot_corner(chains: np.ndarray, param_names: list[str], output_path: Path) -> None:
    """Generate corner plot from MCMC chains."""
    
    # Flatten chains if needed
    if chains.ndim == 3:
        # shape: (nsteps, nwalkers, ndim)
        nsteps, nwalkers, ndim = chains.shape
        chains_flat = chains.reshape(nsteps * nwalkers, ndim)
    else:
        chains_flat = chains
    
    # Create corner plot
    fig = corner.corner(
        chains_flat,
        labels=param_names,
        quantiles=[0.16, 0.5, 0.84],
        show_titles=True,
        title_kwargs={"fontsize": 10},
    )
    
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[OK] Corner plot saved to {output_path}")
    plt.close(fig)


def plot_traces(chains: np.ndarray, param_names: list[str], output_path: Path) -> None:
    """Generate chain traces for convergence diagnostics."""
    
    if chains.ndim == 3:
        nsteps, nwalkers, ndim = chains.shape
    else:
        ndim = chains.shape[1]
        nwalkers = 1
        nsteps = chains.shape[0]
    
    fig, axes = plt.subplots(ndim, 1, figsize=(12, 3 * ndim))
    if ndim == 1:
        axes = [axes]
    
    if chains.ndim == 3:
        for i in range(ndim):
            for j in range(nwalkers):
                axes[i].plot(chains[:, j, i], alpha=0.3, linewidth=0.5)
            axes[i].set_ylabel(param_names[i])
            axes[i].set_xlabel("Step")
    else:
        for i in range(ndim):
            axes[i].plot(chains[:, i], linewidth=0.5)
            axes[i].set_ylabel(param_names[i])
            axes[i].set_xlabel("Step")
    
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[OK] Trace plot saved to {output_path}")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate corner plots and traces for V94 MCMC")
    parser.add_argument("--output-dir", default=None, help="Output directory for results")
    args = parser.parse_args()
    
    # Load results
    print("[INFO] Loading V94 MCMC results...")
    result, chains = load_mcmc_results(args.output_dir)
    
    param_names = result["param_names"]
    output_dir = Path(args.output_dir or (workspace_root() / "results" / "result-analyse")) / "v94_mcmc_cosmo"
    
    # Generate corner plot
    corner_path = output_dir / "v94_corner_plot.png"
    print(f"[INFO] Generating corner plot ({corner_path.name})...")
    plot_corner(chains, param_names, corner_path)
    
    # Generate trace plot
    trace_path = output_dir / "v94_trace_plot.png"
    print(f"[INFO] Generating trace plot ({trace_path.name})...")
    plot_traces(chains, param_names, trace_path)
    
    print("\n[SUCCESS] Plots generated successfully")
    print(f"Corner plot: {corner_path}")
    print(f"Trace plot: {trace_path}")


if __name__ == "__main__":
    main()
