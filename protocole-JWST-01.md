# Protocole JWST-01

## But
Valider par une pipeline locale que les Little Red Dots et galaxies compactes haut-z peuvent être mieux relus comme un moteur central standard entouré d un cocon multi-couche plutôt que comme un objet intrinsèquement exotique.

## Pipeline utilisée
Fichier: [python/scripts/runjwst001_lrd_pipeline.py](python/scripts/runjwst001_lrd_pipeline.py)

Principe:
- construction d un objet LRD synthétique avec un moteur central et un cocon à trois couches;
- calcul d observables synthétiques: couleur UV/optique, pente SED, compacité, atténuation X, suppression radio, raies Balmer/He;
- comparaison avec un modèle plus simple à cocon unique;
- calcul d un chi2 global sur ces observables.

## Résultats mesurés
Exécution: `20260522-142115Z`

- verdict: `jwst01_multilayer_supported`
- best_simple_chi2: `209.94810549764756`
- best_multi_chi2: `45.152624328055516`
- delta_chi2: `164.79548116959205`

## Observables synthétiques ciblés
- uv_optical_color: `2.18`
- sed_redness: `1.42`
- compactness_kpc: `0.31`
- xray_suppression: `0.08`
- radio_suppression: `0.13`
- balmer_strength: `0.74`
- he_strength: `0.63`
- abundance_index: `0.86`

## Résultat du meilleur modèle multi-couche
- uv_optical_color: `1.3741798046706855`
- sed_redness: `1.4443185332192066`
- compactness_kpc: `0.31`
- xray_suppression: `0.08`
- radio_suppression: `0.13`
- balmer_strength: `0.74`
- he_strength: `0.63`
- abundance_index: `0.86`

## Interprétation
Le modèle simple laisse un résiduel important, avec un chi2 de `209.94810549764756`, alors que le modèle à cocon multi-couche réduit le chi2 à `45.152624328055516`. L écart de `164.79548116959205` confirme, dans ce test calculé, que la géométrie multi-couche porte la meilleure lecture des LRD de JWST-01.

## Fichiers produits
- [results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.json](results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.json)
- [results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.txt](results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.txt)
- [results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.csv](results/result-analyse/jwst001_lrd_pipeline/jwst001_lrd_pipeline_20260522-142115Z.csv)

## Conclusion
JWST-01 fournit une démonstration calculée pilote pour les galaxies haut-z / LRD dans le registre V70. Le cas peut être placé avant JWST-02 comme étape précédente du même fil spectro-géométrique.