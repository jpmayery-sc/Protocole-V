# Frozen Dynamic Reference V94

Date: 2026-05-27

This snapshot freezes the calibrated dynamic solver run as the current dynamic reference for V94.

## Run summary
- Command: `python/scripts/v94_cosmo_chi2.py --nwalkers 24 --nsteps 300 --dynamic-solver`
- Solver mode: dynamic
- Verdict: `v94_mcmc_complete`
- Timestamp: 20260527-135206Z

## Reference fit
- Total posterior predictive chi2: 10.05
- H(z) chi2: 0.22
- f_sigma8(z) chi2: 5.37
- S8 chi2: 4.46

## Convergence
- Mean acceptance fraction: 0.329
- Autocorrelation time: about 22 to 24 steps across parameters
- Effective sample size: about 239 to 267 per parameter

## Posterior medians
- alpha_k: 0.602
- alpha_t: 0.731
- alpha_kt: 0.311
- gamma_star: 1.521
- chi2_coupling: 0.113

## Notes
- This is the calibrated dynamic reference, not the historical surrogate baseline.
- The surrogate baseline remains frozen separately in `FROZEN_V94_BASELINE.md`.
- The dynamic branch is now the preferred starting point for further scientific refinement.
