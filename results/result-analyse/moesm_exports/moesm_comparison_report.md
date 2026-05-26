MOESM workbook comparison
timestamp: 2026-05-15 12:51:37Z

1. Role split
- MOESM2 is figure-oriented: compact tabular data, fits, and simulations for Fig2a to Fig2d.
- MOESM3 is grid-oriented: large pcolormesh-ready surfaces with gamma_r, gamma_im, and W.

2. Sheet-level comparison
- MOESM2 sheets:
  - Fig2a-Experiment: rows=183, cols=5, numeric_range=[0.003059028602487912, 303.6]
  - Fig2a-Fits: rows=50, cols=4, numeric_range=[0.5, 203.6]
  - Fig2a-Simulation: rows=60, cols=2, numeric_range=[0.5000516719256158, 298.6]
  - Fig2b-Experimet: rows=19, cols=4, numeric_range=[0.0189513505403318, 1000.0]
  - Fig2b-Theory: rows=100, cols=4, numeric_range=[0.0, 1000.0]
  - Fig2c-Experiment: rows=150, cols=5, numeric_range=[0.0, 1.0]
  - Fig2c-Fit: rows=400, cols=4, numeric_range=[-0.152, 1.098]
  - Fig2d-Experiment: rows=14, cols=5, numeric_range=[-0.0561336872216656, 1.04582068461389]
  - Fig2d-Fit: rows=50, cols=2, numeric_range=[0.0, 1.024871982800574]
- MOESM3 sheets:
  - sqz_exp: rows=194481, cols=3, numeric_range=[-14.77602791224193, 14.77602791224193]
  - sqz_sim: rows=194481, cols=3, numeric_range=[-4.0, 4.0]
  - trisqz_exp: rows=194481, cols=3, numeric_range=[-14.77602791224193, 14.77602791224193]
  - trisqz_sim: rows=194481, cols=3, numeric_range=[-4.0, 4.0]
  - quadsqz_exp: rows=203401, cols=3, numeric_range=[-15.39247137665673, 15.39247137665673]
  - quadsqz_sim: rows=203401, cols=3, numeric_range=[-4.0, 4.0]
  - README: rows=2, cols=1, numeric_range=[None, None]

3. Practical reading for theory
- Use MOESM2 for direct figure reconstruction, parameter extraction, and trend checks.
- Use MOESM3 for contour/heatmap reconstruction, grid-sensitive interpolation tests, and surface topology analysis.
- The two files are complementary rather than redundant.

