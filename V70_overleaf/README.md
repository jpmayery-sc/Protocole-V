# V70 Overleaf project

Projet LaTeX compilable pour la consolidation finale du modèle K/T/Y + D1/D2 + V_ent.

## Fichiers principaux
- `main.tex`
- `tables/`
- `figures/`
- `appendices/`

## Version figée
- Baseline figée avant solveur dynamique: `FROZEN_V94_BASELINE.md`
- Le manuscrit V94 garde désormais la version surrogate comme référence historique.
- Référence dynamique calibrée: `FROZEN_V94_DYNAMIC_REFERENCE.md`

## Compilation
Ouvrir `main.tex` dans Overleaf ou compiler localement avec `pdflatex` / `latexmk`.

## Solveur dynamique
- Nouveau module: `python/scripts/v95_dynamic_solver.py`
- Mode V94 dynamique optionnel: `python/scripts/v94_cosmo_chi2.py --dynamic-solver`
- Mode V94 par défaut: surrogate / bridge historique, pour préserver la reproductibilité du baseline figé

## Contenu
Le document intègre les résultats numériques consolidés de V60--V61:
- `chi^2_fsigma8_with_ent = 1.84`
- `chi^2_fsigma8_noent = 9.62`
- `Delta chi^2_fsigma8 = 7.78`
- `S8_with_ent = 0.776`
- `S8_noent = 0.812`
- `chi^2_H = 2.11`