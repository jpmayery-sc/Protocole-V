# Protocole V

Ce dépôt rassemble le manuscrit V70, les protocoles associés, les scripts de calcul et les résultats consolidés utilisés pour la préparation de la version publiable.

## Contenu principal
- `V70_overleaf/`: manuscrit LaTeX principal, figures, tableaux et annexes.
- `python/`: scripts d'analyse et utilitaires de calcul.
- `results/`: sorties numériques, comparaisons et synthèses.
- `data/`: jeux de données et notes de provenance.
- `protocole de test*.txt` et `ProtocoleV*.md`: historique des protocoles et variantes.

## Manuscrit
Le point d’entrée du document est `V70_overleaf/main.tex`.

Pour compiler localement:
1. ouvrir `V70_overleaf/main.tex` dans Overleaf ou un éditeur LaTeX;
2. lancer `latexmk -pdf main.tex` depuis `V70_overleaf/`;
3. vérifier que les chemins vers `figures/`, `tables/` et `appendices/` sont résolus.

## Reproductibilité
Les calculs et figures consolidés ont été préparés à partir de données publiques citées dans l’annexe C du manuscrit. Les fichiers locaux du dépôt servent à la reproduction, à la validation et à l’archivage des runs.

## GitHub
Le dépôt distant cible est prévu pour recevoir ce contenu une fois les accès confirmés. Le lien public sera ensuite ajouté dans le manuscrit.