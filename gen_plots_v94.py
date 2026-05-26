#!/usr/bin/env python
"""Quick V94 plots generation - non-interactive."""

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import corner

# Paths
ws = Path("d:/Privé/Tout ne fait qu'un/experience/experience 4")
v94_dir = ws / "results" / "result-analyse" / "v94_mcmc_cosmo"

# Load latest results
json_files = sorted(v94_dir.glob("v94_mcmc_cosmo_*.json"))
latest_json = json_files[-1]
with open(latest_json) as f:
    result = json.load(f)

# Load chains
chain_files = sorted(v94_dir.glob("mcmc_chains_*.npy"))
latest_chains = chain_files[-1]
chains = np.load(latest_chains)
print(f"[INFO] Loaded chains shape: {chains.shape}")

# Flatten if needed
if chains.ndim == 3:
    nsteps, nwalkers, ndim = chains.shape
    chains_flat = chains.reshape(nsteps * nwalkers, ndim)
else:
    chains_flat = chains

# Generate corner plot
param_names = result["param_names"]
print("[INFO] Generating corner plot...")
fig = corner.corner(
    chains_flat,
    labels=[f"${p}$" if len(p) > 1 else p for p in param_names],
    quantiles=[0.16, 0.5, 0.84],
    show_titles=True,
    title_kwargs={"fontsize": 9},
)
corner_path = v94_dir / "v94_corner_plot.png"
fig.savefig(corner_path, dpi=150, bbox_inches="tight")
print(f"[OK] Corner plot: {corner_path.name}")
plt.close(fig)

# Generate traces
print("[INFO] Generating trace plot...")
fig, axes = plt.subplots(ndim, 1, figsize=(12, 2.5 * ndim))
if ndim == 1:
    axes = [axes]

for i in range(ndim):
    for j in range(min(nwalkers, 10)):  # Plot subset for clarity
        axes[i].plot(chains[:, j, i], alpha=0.3, linewidth=0.5)
    axes[i].set_ylabel(param_names[i])
    axes[i].set_xlabel("Step")

fig.tight_layout()
traces_path = v94_dir / "v94_traces.png"
fig.savefig(traces_path, dpi=150, bbox_inches="tight")
print(f"[OK] Trace plot: {traces_path.name}")
plt.close(fig)

print("\n[VERDICT] V94 Plots generation complete!")
