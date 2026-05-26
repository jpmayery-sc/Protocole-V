# Protocole JWST-04

## But
Valider par une pipeline locale que les tensions sur M*, SFR, luminosités et densités de galaxies haut-z deviennent plus cohérentes après homogénéisation baryonique et relecture géométrique K/T/Y + D1/D2.

## Pipeline utilisée
Fichier: [python/scripts/runjwst004_galaxy_formation_pipeline.py](python/scripts/runjwst004_galaxy_formation_pipeline.py)

Principe:
- homogénéisation baryonique d un catalogue JWST synthétique;
- comparaison des masses stellaires, SFR, luminosités et densités à un modèle compact géométrique;
- calcul de chi2 séparés pour M*, SFR, luminosités et densités.

## Résultats mesurés
Exécution: `20260522-153925Z`

- verdict: `jwst04_homogenized_supported`
- chi2_M*: `188.26058596033286`
- chi2_SFR: `14.22121616609834`
- chi2_L: `140.4091744944848`
- chi2_n: `24.70622883468115`
- baseline_total_chi2: `2636270.6671180255`
- total_chi2: `367.5972054555972`
- delta_chi2: `2635903.06991257`

## Observables homogénéisées
- mean_M*: `4000000000.0`
- mean_SFR: `32.0`
- mean_L: `17880000000.0`
- mean_n: `0.27`

## Interprétation
La réanalyse baryonique réduit de façon massive l écart au modèle de référence, avec un gain global de `2635903.06991257` sur le chi2 total. Les plus grands résidus restent la masse stellaire et la luminosité, alors que la SFR et la densité sont déjà bien mieux contrôlées.

## Fichiers produits
- [results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.json](results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.json)
- [results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.txt](results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.txt)
- [results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.csv](results/result-analyse/jwst004_galaxy_formation_pipeline/jwst004_galaxy_formation_pipeline_20260522-153925Z.csv)

## Conclusion
JWST-04 fournit une démonstration calculée pilote pour la formation des galaxies dans le registre V70. Le cas peut être placé avant JWST-03 comme étape préparatoire du même fil JWST.