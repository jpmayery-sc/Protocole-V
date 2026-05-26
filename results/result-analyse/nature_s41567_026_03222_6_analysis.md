# Analyse des fichiers MOESM2 et MOESM3

Source: article Nature `s41567-026-03222-6`.

## Résumé

Les deux fichiers téléchargés sont cohérents et exploitables.

- [MOESM2.xlsx](../../downloaded_xlsx/MOESM2.xlsx) contient des données compactes, organisées par figure, avec des expériences, des ajustements et des simulations pour les figures 2a à 2d.
- [MOESM3.xlsx](../../downloaded_xlsx/MOESM3.xlsx) contient des grilles denses au format `gamma_r`, `gamma_im`, `W`, manifestement destinées aux cartes `pcolormesh`.

## MOESM2.xlsx

Structure observée:

- 9 feuilles au total.
- Feuilles principales: `Fig2a-Experiment`, `Fig2a-Fits`, `Fig2a-Simulation`, `Fig2b-Experimet`, `Fig2b-Theory`, `Fig2c-Experiment`, `Fig2c-Fit`, `Fig2d-Experiment`, `Fig2d-Fit`.

Points importants:

- `Fig2a-Experiment` contient 3 séries distinctes: `th_data`, `ds_phi_m`, `dl_phi_m_plus_pi2`.
- `Fig2b-Experimet` contient 2 séries de décalage, `Δ = 50 kHz` et `Δ = 100 kHz`.
- `Fig2c-Experiment` contient 2 conditions initiales: `start in |downarrow>` et `start in |uparrow>`.
- `Fig2d-Experiment` est une table simple sans étiquette de série explicite dans la première colonne.

Observations de qualité:

- Le classeur est propre et lisible.
- Il y a une coquille mineure dans le nom de feuille `Fig2b-Experimet`.
- Quelques en-têtes portent une colonne vide finale `None`, mais cela ne gêne pas l’exploitation des données.

## MOESM3.xlsx

Structure observée:

- 7 feuilles au total.
- 6 feuilles de données: `sqz_exp`, `sqz_sim`, `trisqz_exp`, `trisqz_sim`, `quadsqz_exp`, `quadsqz_sim`.
- 1 feuille `README` qui précise que chaque ligne correspond exactement à un point de grille pour `pcolormesh`, sans interpolation.

Résolution des grilles:

- `sqz_exp`, `sqz_sim`, `trisqz_exp`, `trisqz_sim`: grilles `441 x 441`, soit 194481 points.
- `quadsqz_exp`, `quadsqz_sim`: grilles `451 x 451`, soit 203401 points.

Plages numériques:

- Les feuilles expérimentales couvrent environ `[-14.776, 14.776]` pour `sqz` et `trisqz`, et `[-15.392, 15.392]` pour `quadsqz`.
- Les feuilles de simulation couvrent `[-4, 4]`.
- Les valeurs `W` restent du même ordre de grandeur dans chaque paire exp/sim, avec des maxima autour de `0.15` à `0.20` selon la feuille.

## Conclusion

Le téléchargement est bon: les deux fichiers ne sont pas corrompus et ils correspondent à deux niveaux d’exploitation différents.

- [MOESM2.xlsx](../../downloaded_xlsx/MOESM2.xlsx) sert de base aux figures et aux ajustements.
- [MOESM3.xlsx](../../downloaded_xlsx/MOESM3.xlsx) sert de base aux cartes de densité sur grille fine.

Si tu veux, l’étape suivante peut être soit une extraction en tableaux CSV, soit une comparaison visuelle figure par figure avec les scripts du workspace.