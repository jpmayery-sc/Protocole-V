# Tube Theory Numeric Test

## Objective

This document defines a strict numerical test for the Tube Theory using existing published data only.

The goal is to determine whether a geometric term adds a measurable improvement over standard physics without introducing hidden free parameters.

If no robust gain appears, the theory is invalidated as a physical theory and kept only as an interpretive language.

## Decision Rule

Compare two models on the same data:

- Model A: standard physics, with all known corrections already allowed.
- Model B: standard physics plus one geometric term.

Model B is:

phi_total = phi_std + lambda * Omega

Where:

- Omega is one fixed geometric invariant.
- lambda is a single global coefficient, fitted once and then frozen.

The same lambda must improve multiple independent datasets.

## Allowed datasets

Choose at least two among:

1. Published interferometry data
- Sagnac
- optical rings
- coiled fibers
- twisted cavities

2. Skin effect data
- penetration depth versus frequency
- copper, aluminum, iron
- high-frequency residuals and extra losses

3. Strong induction and magnetic saturation
- B(H) curves
- published hysteresis loops
- saturation thresholds

4. Existing atomic interferometry
- atom gravimeters
- atomic loops
- inertial phase experiments

## Allowed definitions for Omega

Choose one Omega definition only for the whole run.

### Omega_1: integrated torsion

Omega_1 = integral_0^L tau(s) ds

Use when the path geometry is known well enough to compute torsion along the curve.

### Omega_2: normalized winding number

Omega_2 = N_turns

Use when the dataset naturally provides a winding count around a reference axis.

### Omega_3: quadratic geometric deviation

Omega_3 = (1 / L) * integral_0^L ||r(s) - r_lin(s)||^2 ds

Use when a real trajectory can be compared with its straight-line surrogate.

Mixing Omega definitions across datasets is forbidden.

## Protocol

1. Fit the standard model on each dataset and compute residuals.
2. Compute Omega_i for each point.
3. Fit lambda on one dataset only.
4. Freeze lambda.
5. Recompute residuals on the other datasets with the same lambda.
6. Compare RMSE, reduced chi^2, AIC, and BIC before and after.

## Validation criteria

The Tube Theory is provisionally supported only if all of the following hold:

- RMSE decreases by at least 20 percent.
- reduced chi^2 decreases robustly.
- the improvement appears on at least two independent datasets.
- the same lambda is used everywhere.
- AIC or BIC remains favorable despite the extra parameter.

## Immediate invalidation conditions

Invalidate the theory immediately if any of the following occurs:

- the gain is smaller than the experimental noise;
- lambda changes from one system to another;
- the improvement exists only on the fit dataset;
- AIC or BIC penalizes the extra parameter.

## Required report

The test report must contain:

- the chosen Omega definition;
- the single fitted lambda value;
- before/after tables for RMSE and reduced chi^2;
- the final binary verdict: SUPPORTED or INVALIDATED.

No philosophical interpretation is needed.

## Repository structure for the series

This is the suggested numeric test layout:

```text
tube-test/
|-- data/
|   |-- interferometry/
|   |-- induction/
|   `-- skin_effect/
|-- omega/
|   |-- omega_torsion.py
|   |-- omega_winding.py
|   `-- omega_deviation.py
|-- models/
|   |-- model_standard.py
|   `-- model_tube.py
|-- analysis/
|   |-- fit_lambda.py
|   |-- cross_validation.py
|   `-- metrics.py
|-- results/
|   |-- tables/
|   `-- figures/
`-- report/
    `-- verdict.md
```

## README summary

The series exists to answer one question only: does a fixed geometric term improve existing data in a way that survives cross-validation?

If not, the Tube Theory is rejected as a physical model.