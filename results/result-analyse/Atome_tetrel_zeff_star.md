# Tetrel: Zeff* comme variable structurante

Ce point formalise la seconde question tetrel encore ouverte: comment utiliser Zeff* comme variable de structure separée sans confondre ce test avec l ionisation elle-meme.

## Constat experimental

- [python/scripts/tetrel_subseries_zeff_star_check.py](../../python/scripts/tetrel_subseries_zeff_star_check.py) est supporte.
- Sous-serie legere C -> Ge: RMSE mass 13.021568, RMSE Zeff 9.501792, RMSE Zeff★ 9.238054, RMSE corrige 0.003144.
- Sous-serie lourde Ge -> Pb: RMSE mass 4.670225, RMSE Zeff 3.235367, RMSE Zeff★ 3.143596, RMSE corrige 0.000000.
- Zeff★ bat mass et Zeff brut dans les deux sous-series.

## Pourquoi Zeff★ doit rester un test separé

- Zeff★ n est pas l ionisation: il combine la lecture de charge effective avec des corrections de regime.
- L ionisation reste une observable propre, utile pour le controle, mais elle ne suffit pas a elle seule a organiser la sous-serie.
- Le bon test est donc de verifier que Zeff★ apporte une information structurante nouvelle et reproductible.

## Formulation de travail

- Zeff★ est supporte sur les deux sous-series tetrel.
- Le critere rayon / Zeff★ doit rester distinct de l ionisation.
- Le test Zeff★ doit montrer qu il apporte mieux que mass et Zeff brut, puis qu il reste stable apres correction.

## Sortie attendue

- Cette note sert de specification de test pour le bloc tetrel Zeff★.
- Elle fixe le prochain jalon: transformer Zeff★ en test executable distinct de l ionisation.