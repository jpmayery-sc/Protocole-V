# Frozen Baseline V94

Date: 2026-05-27

This snapshot freezes the current manuscript and pipeline state before the dynamic solver build.

## Frozen state
- Manuscript: V70_overleaf/main.tex
- Annex V94: semi-phenomenological MCMC with bridge-based projections
- Current cosmology pipeline: surrogate / bridge model, not a full dynamic ODE solver
- Current reproducibility assets: tables/, figures/, appendices/

## Notes
- The baseline keeps the current outputs and wording as the reference point.
- The next development step is the dynamic solver implementation, initially behind a feature flag so the surrogate path remains reproducible.
- The calibrated dynamic reference run is documented separately in `FROZEN_V94_DYNAMIC_REFERENCE.md`.
