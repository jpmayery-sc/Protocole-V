V94 MCMC Cosmological Parameter Estimation
=============================================

Description
-----------
This directory contains outputs from the V94 MCMC run, which performs a complete
Bayesian parameter estimation of the K/T/Y + D1/D2 + L_ent cosmological model
using observables: H(z), f_sigma8(z), S8.

MCMC Configuration
------------------
- Algorithm: Affine-invariant ensemble sampler (emcee)
- Walkers: 32
- Steps: 2000 (20% burn-in discarded)
- Parameters: {alpha_k, alpha_t, alpha_kt, gamma_star, chi2_coupling}
- Data: Consolidated from V92 (6 H(z) pts, 7 f_sigma8 pts, 1 S8 point)

Files
-----
- v94_mcmc_cosmo_{timestamp}.json
  Full MCMC results: parameter statistics, mcmc metadata, chain file path

- v94_mcmc_cosmo_{timestamp}.txt
  Human-readable summary: parameter medians, 68% and 95% confidence intervals

- mcmc_chains_{timestamp}.npy
  Raw MCMC chain samples (shape: nsteps*nwalkers, ndim, requires numpy to load)

How to Run
----------
python python/scripts/v94_cosmo_chi2.py --nwalkers 32 --nsteps 2000 --output-dir results/result-analyse

This command will:
1. Load H(z) and f_sigma8(z) data from v92_cosmo_chi2/data/
2. Perform MCMC sampling
3. Save results to v94_mcmc_cosmo/ directory
4. Print summary JSON to stdout

Post-processing
---------------
To generate corner plots and parameter correlations, use the chains file:

  import numpy as np
  chains = np.load('mcmc_chains_{timestamp}.npy')  # shape: (nsamples, ndim)
  # Use corner.py or getdist for visualization

Validation
----------
V94 verdict is 'v94_mcmc_complete' if:
- MCMC has converged (visual inspection of chain traces)
- Parameters are compatible with V92/V93B (< 10% deviation)
- Correlation structure is physically reasonable
- Output files are reproducible on re-run

Reproducibility
---------------
This run depends on:
- python/scripts/v93b_c_em_lagrangian.py (bridge computation)
- results/result-analyse/v92_cosmo_chi2/data/hubble_observations.csv
- results/result-analyse/v92_cosmo_chi2/data/fs8_observations.csv
- Python packages: emcee, numpy, pandas

For full provenance, see manuscript V70_overleaf/main.tex appendix I (V94).
