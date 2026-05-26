# Tetrel a formaliser

Ce fichier rassemble l etat actuel des tests tetrel qui restent a formaliser proprement dans le cadre atomique.

## 1. Variante plus fine pour la sous-serie tetrel

- [x] formaliser pourquoi la correction k/L n efface pas le besoin d un critere structurel supplementaire: [results/result-analyse/Atome_tetrel_correction_structurelle.md](Atome_tetrel_correction_structurelle.md)

- status actuel: [python/scripts/tetrel_subseries_k_l_correction_check.py](../../python/scripts/tetrel_subseries_k_l_correction_check.py) est supporte, avec amelioration nette des residus dans la sous-serie legere et la sous-serie lourde.
- evidence legere: le RMSE passe de 9.501792 a 0.004807 sur C -> Ge.
- evidence lourde: le RMSE passe de 3.235367 a 0.000134 sur Ge -> Pb.
- point restant: garder la correction k/L comme ajustement utile, mais continuer a chercher un critere structurel distinct.

## 2. Variante Zeff★ tetrel

- [x] formaliser le critere rayon / Zeff★ comme test separé, avec ionisation conservée comme observable distincte: [results/result-analyse/Atome_tetrel_zeff_star.md](Atome_tetrel_zeff_star.md)

- status actuel: [python/scripts/tetrel_subseries_zeff_star_check.py](../../python/scripts/tetrel_subseries_zeff_star_check.py) est supporte, et Zeff★ bat mass et Zeff brut dans les deux sous-series.
- evidence legere: RMSE mass 13.021568, RMSE Zeff 9.501792, RMSE Zeff★ 9.238054, RMSE corrige 0.003144.
- evidence lourde: RMSE mass 4.670225, RMSE Zeff 3.235367, RMSE Zeff★ 3.143596, RMSE corrige 0.000000.
- point restant: conserver l ionisation comme observable distincte, mais utiliser Zeff★ comme variable structurante separée.

## 3. Extension potentielle de famille ou de periode

- [x] definir le jeu minimal de cas si une famille supplementaire ou une periode supplementaire devient necessaire: [results/result-analyse/Atome_tetrel_extension_famille_periode.md](Atome_tetrel_extension_famille_periode.md)

- statut actuel: aucun contre-exemple nouveau n impose encore une extension.
- point restant: n ouvrir l extension qu en presence d un vrai contre-exemple, puis formaliser le jeu minimal de cas.

- test executable associe: [python/scripts/tetrel_extension_famille_periode_check.py](../../python/scripts/tetrel_extension_famille_periode_check.py)

## Regle de cloture

- [x] considerer le bloc tetrel comme complet quand la sous-serie plus fine et Zeff★ sont traduits en tests executables avec verdict explicite.