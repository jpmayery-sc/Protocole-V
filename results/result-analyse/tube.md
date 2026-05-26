# tube

## But
Suivre la serie de tests tube de facon numerique, tracee et prudente.

## Protocole
- Un seul Omega fixe pour toute la serie.
- Un seul fit de lambda, puis lambda est fige.
- Comparer le modele standard et le modele standard + terme geometrique.
- Juger avec RMSE, chi2 reduit, AIC et BIC.
- Invalider si le gain n'est pas robuste sur les jeux de validation.

## Jeux de donnees a suivre
- one_fixed_damper : reference hysteresis / mecanique.
- test_experiments : troisieme jeu telecharge pour prudence.
- core_loss_mhz : reference pertes magnetiques haute frequence.
- inp_Test_experiments.json : fichier compagnon du jeu test_experiments.

## Tests a realiser
1. Verifier que chaque fichier brut est lisible et que sa structure est stable.
2. Verifier que le manifeste pointe vers les bons chemins locaux.
3. Verifier que le runner charge bien le manifeste reel et pas le template.
4. Verifier que la serie produit un verdict pour chaque jeu declare.
5. Verifier que Omega reste identique sur tous les tests.
6. Verifier que lambda est estime une seule fois puis fige.
7. Comparer les scores du modele standard et du modele tube.
8. Verifier la robustesse sur validation croisee.
9. Verifier la stabilite des gains sur les trois jeux.
10. Rejeter le modele si le gain disparait sur un jeu ou une sous-partie.

## Scripts de validation
- `tube_test/scripts/validate_tube_manifest.py` : controle la forme du manifeste.
- `tube_test/scripts/validate_tube_data.py` : controle l'existence et la lisibilite des fichiers.
- `tube_test/scripts/validate_tube_metrics.py` : valide les metriques sur un cas synthetique.
- `tube_test/scripts/validate_tube_real_metrics.py` : applique les metriques aux donnees reelles du tube.
- `tube_test/scripts/validate_tube_suite.py` : execute la validation de bout en bout.

## Etat reel des donnees
- `One_fixed_damper.json` et `Test_experiments.json` sont structures comme un objet de series, chaque cle contenant une liste de cas avec `velocity`, `time`, `force` et `displace`.
- Le validateur reel utilise le premier cas de chaque serie pour les mesures courantes.
- Le validateur reel passe et confirme un gain du modele tube sur les deux jeux JSON.
- `core_loss_mhz` reste controle via le nombre de lignes CSV lues.

## Ordre d'execution
1. `validate_tube_manifest.py`
2. `validate_tube_data.py`
3. `validate_tube_metrics.py`
4. `validate_tube_real_metrics.py`
5. `validate_tube_suite.py`
6. Revue du verdict final.

## Etat actuel apres reprise
- Le manifeste reel `tube_test/data/manifest.json` existe et declare 3 jeux de donnees.
- Les donnees attendues sont presentes: `One_fixed_damper.json`, `Test_experiments.json`, `inp_Test_experiments.json` et `MHzCoreLoss.csv`.
- Les scripts de validation sont en place pour le manifeste, les donnees, les metriques reelles et la suite complete.
- `tube_test/scripts/run_tube_suite.py` orchestre maintenant la validation reelle et ecrit un resume de suite supporte.
- `tube_test/report/verdict.md` reste un gabarit avec des champs `TBD`.
- `tube_test/results/` contient maintenant un resume real de suite, pas seulement le gabarit template.

## Validation reelle apres reprise
- `validate_tube_manifest.py` passe et confirme un manifeste valide avec 3 jeux declares.
- Les scripts `validate_tube_data.py`, `validate_tube_metrics.py`, `validate_tube_real_metrics.py` et `validate_tube_suite.py` s'executent directement depuis leur chemin fichier apres bootstrap du chemin Python.
- `validate_tube_real_metrics.py` montre un avantage tube sur les deux jeux JSON, plus un controle positif sur `core_loss_mhz`.
- `validate_tube_suite.py` retourne maintenant `overall_verdict: "supported"` avec 3/3 jeux valides et un vrai chemin de sortie `tube_theory_suite_summary.json` / `.txt`.

## Lecture courte
La base est maintenant valide de bout en bout pour la suite tube: manifeste, donnees, metriques et orchestration passent, et l'execution directe des scripts tube fonctionne aussi.

## Verdict final
- Verdict: `supported`.
- La suite tube passe en execution reelle avec 3/3 jeux valides.
- La sortie finale est ecrite dans `tube_test/results/tube_theory_suite_summary.json` et `tube_test/results/tube_theory_suite_summary.txt`.