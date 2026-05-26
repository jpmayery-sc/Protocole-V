# Tetrel: correction k/L et critere structurel

Ce point formalise la premiere question tetrel encore ouverte: pourquoi la correction k/L, bien que tres efficace sur les residus, ne suffit pas a elle seule pour clore la lecture structurelle.

## Constat experimental

- [python/scripts/tetrel_subseries_k_l_correction_check.py](../../python/scripts/tetrel_subseries_k_l_correction_check.py) est supporte.
- Sous-serie legere C -> Ge: le RMSE passe de 9.501792 a 0.004807.
- Sous-serie lourde Ge -> Pb: le RMSE passe de 3.235367 a 0.000134.
- La tendance en rayon reste monotone dans les deux sous-series.

## Pourquoi cela ne suffit pas

- La correction k/L agit comme un meilleur ajustement de residus, pas comme un critere physique independant qui remplace la lecture structurelle.
- Le fait qu un fit soit meilleur ne prouve pas qu il capture seul l organisation de la sous-serie.
- Le besoin d un critere supplementaire reste pertinent tant qu il faut distinguer l ajustement numerique d une vraie variable organisatrice.

## Formulation de travail

- La correction k/L est utile.
- La correction k/L ne remplace pas le besoin d un critere structurel separé.
- Le test future doit verifier si une variable de structure explicite apporte une information nouvelle par rapport a k/L seul.

## Sortie attendue

- Cette note sert de pont vers le test Zeff★ tetrel.
- Elle fixe le point suivant: on conserve la correction k/L, mais on continue a chercher un critere structurel explicite.