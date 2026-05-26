# Protocole JWST-08

## But
Tester si les BH précoces dormants peuvent être interprétés comme des SMBH en cycle d'activité, contrôlé par la géométrie D1/D2, avec une Broad Hα faible mais détectable, une luminosité résiduelle faible et un ratio MBH/M* élevé.

## Pipeline utilisée
Fichier: [python/scripts/runjwst008_dormant_bh_pipeline.py](python/scripts/runjwst008_dormant_bh_pipeline.py)

Principe:
- homogénéiser les observables sur Broad Hα, la luminosité bolométrique, le ratio MBH/M* et la compacité des hôtes;
- comparer ces observables à un modèle K/T/Y + D1/D2;
- simuler une phase dormante à faible inflow;
- calculer des chi2 séparés pour Broad Hα, Lbol, ratio et compacité.

## Résultats mesurés
Exécution: `20260522-164526Z`

- verdict: `jwst08_dormant_bh_supported`
- chi2_broad_ha: `0.05046266071494085`
- chi2_lbol: `19.438752773412677`
- chi2_ratio: `1.1257168133162367`
- chi2_compactness: `4.379792527879032`
- baseline_total_chi2: `233.71701274104754`
- total_chi2: `24.99472477532289`
- delta_chi2: `208.72228796572466`
- mean_broad_ha_log_hom: `3.1`
- mean_lbol_log_hom: `42.104`
- mean_ratio_hom: `0.019`
- mean_compactness_hom: `0.78`

## Fichiers produits
- [results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.json](results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.json)
- [results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.txt](results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.txt)
- [results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.csv](results/result-analyse/jwst008_dormant_bh_pipeline/jwst008_dormant_bh_pipeline_20260522-164526Z.csv)

## Conclusion
JWST-08 est retenu comme démonstration calculée pilote pour les BH précoces dormants dans le registre V70. Le verdict de la pipeline est `jwst08_dormant_bh_supported` et le gain global est `delta_chi2=208.72228796572466`.