# Validation Electron — méthode bootstrap et interprétation

Ce fichier décrit la méthode utilisée pour produire les statistiques de validation (test T5) et donne une interprétation des résultats actuels.

Fichiers produits importants
- `results/electron_validation_results_with_bootstrap_20260505-114210Z.json` — résultats de validation enrichis (bootstrap).  
- `results/electron_validation_bootstrap_report_20260505-114210Z.txt` — rapport textuel synthétique (p-values et IC).  

Commande pour rejouer le bootstrap (par défaut nsamples=3000) :

```bash
python scripts/bootstrap_t5_stats.py --nsamples 10000 --seed 20260505
```

Protocole résumé
- On agrège pour chaque `MIN_NEUTRON` les paires observées (`|Ce|`, `Cint_n`) depuis `results/sweep_all_*.json`.  
- On calcule la corrélation de Pearson observée `r_obs`.  
- On effectue `nsamples` rééchantillonnages bootstrap (tirage avec remise des indices) des paires et on calcule la distribution bootstrap de `r`.  
- On estime la p‑value two‑sided comme la proportion de `|r_boot| >= |r_obs|`.  
- On calcule l'IC 95% par percentiles de la distribution bootstrap.

Interprétation des résultats actuels
- Les rapports récents montrent des valeurs observées de `r_obs` assez élevées (par ex. pour `MIN_NEUTRON=29`, `r_obs ≈ 0.8896`).  
- Cependant, la taille d'échantillon utilisée par point `MIN_NEUTRON` est très petite (`n = 3` dans les données actuelles). Avec si peu d'observations :
  - Les intervalles de confiance bootstrap sont souvent `NaN` (impossibilité numérique liée à variance nulle dans certains rééchantillonnages).  
  - Les p‑values bootstrap sont élevées (p ≫ 0.05), indiquant qu'on ne peut pas rejeter l'hypothèse nulle avec ces données.

Conséquence
- Malgré des corrélations observées élevées, la signification statistique n'est pas démontrée avec l'échantillonnage actuel. Les résultats sont donc suggestifs mais non confirmatoires.

Recommandations pratiques
1. Augmenter le nombre d'exécutions/variantes par configuration (`n` par `MIN_NEUTRON`) — viser au moins 10–20 points pour une bootstrap fiable.  
2. Si l'augmentation de `n` n'est pas possible, utiliser un test de permutation exact (si applicable) ou calculer p‑values via méthodes non paramétriques spécifiques.  
3. Calculer intervalles de confiance par bootstrap bias‑corrected et/ou faire un bootstrap stratifié si des facteurs confondants existent.  
4. Présenter les figures (déjà générées dans `results/`) et ajouter les p‑values/IC aux tables récapitulatives du rapport.

Notes sur les NaN observés
- Les `NaN` dans les IC proviennent généralement d'échantillons où la variance d'une des variables est nulle sur certains tirages bootstrap ; ceci est cohérent avec `n` très petit et/ou données constantes pour certaines configurations.

Contact
- Si vous validez que l'on augmente `nsamples` ou que l'on produit un sweep plus dense, je peux lancer automatiquement les expériences supplémentaires et mettre à jour les rapports.
# Validation automatique du document `Electron-2.txt`

Ce fichier explique comment exécuter localement la validation automatisée des affirmations présentes dans `Electron-2.txt`.

Prérequis
- Python (idéalement la même version que l'environnement virtuel `.venv`).
- Le dépôt cloné et activé dans l'environnement virtuel :

```powershell
& ".venv\Scripts\Activate.ps1"
```

Exécution rapide

```bash
python scripts/validate_electron_document.py
```

Sorties
- `results/electron_validation_results_<timestamp>.json` : résultats détaillés des tests T1–T5.
- `results/electron_validation_report_<timestamp>.txt` : rapport humain synthétique.

Notes
- Le script réutilise `scripts/run_triangles_with_params.py` pour exécuter les expériences numériques. Assurez-vous que ce script fonctionne dans votre env local.
- Le workflow GitHub Actions (si activé) exécute périodiquement cette validation et pousse les résultats dans le dépôt.

Contact
- Pour modifications ou extension des tests, éditez `scripts/validate_electron_document.py`.
