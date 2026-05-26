# Tetrel: extension potentielle de famille ou de periode

Ce point formalise la derniere question tetrel encore ouverte: que faire si un contre-exemple impose d etendre la famille ou la periode de travail.

Le test executable correspondant est [python/scripts/tetrel_extension_famille_periode_check.py](../../python/scripts/tetrel_extension_famille_periode_check.py).

## Etat actuel

- Aucun contre-exemple nouveau n impose encore une extension.
- La sous-serie tetrel reste lisible avec la correction k/L et avec Zeff★ comme variable structurante.
- Le bloc tetrel peut donc rester ferme tant que les cas actuels suffisent.
- Verdict courant du script: extension non requise.

## Validation recente

- [python/scripts/tetrel_subseries_k_l_correction_check.py](../../python/scripts/tetrel_subseries_k_l_correction_check.py) -> supported.
- [python/scripts/tetrel_subseries_zeff_star_check.py](../../python/scripts/tetrel_subseries_zeff_star_check.py) -> supported.
- [python/scripts/tetrel_extension_famille_periode_check.py](../../python/scripts/tetrel_extension_famille_periode_check.py) -> supported.

Conclusion pratique: il ne reste rien de bloquant a valider pour le bloc tetrel actuel.

## Quand ouvrir une extension

- ouvrir une extension seulement si un nouvel element brise la monotonie ou la regularite observee.
- ouvrir une extension seulement si la lecture D1 / D2 / D3 / D4 ne suffit plus pour expliquer le cas.
- ouvrir une extension seulement si le nouvel element n est pas absorbe par les correctifs tetrel deja valides.

## Jeu minimal de cas

- definir le plus petit ensemble de cas qui montre le contre-exemple.
- garder un cas de controle stable dans la famille deja valide.
- comparer la nouvelle branche au referentiel tetrel deja etabli.

## Sortie attendue

- si aucune anomalie nouvelle n apparait, ne rien ajouter.
- si une anomalie nouvelle apparait, formaliser la branche minimale necessaire puis la traduire en test executable.