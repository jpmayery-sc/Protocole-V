# Protocole JWST-07

## But
Tester si la croissance rapide des SMBH précoces peut être expliquée par une géométrie d'alimentation D1/D2, sans seeds lourds ni super-Eddington prolongé, tout en gardant des ratios MBH/M* et des luminosités bolométriques compatibles avec les observations JWST.

## Pipeline utilisée
Fichier: [python/scripts/runjwst007_smbh_pipeline.py](python/scripts/runjwst007_smbh_pipeline.py)

Principe:
- homogénéiser les observables SMBH sur la masse du trou noir, la luminosité bolométrique, le ratio MBH/M* et la compacité des hôtes;
- comparer ces observables à un modèle K/T/Y + D1/D2;
- intégrer une fenêtre de croissance de 300 à 600 Myr selon le redshift;
- calculer des chi2 séparés pour MBH, Lbol, ratio et compacité.

## Résultats mesurés
Exécution: `20260522-164213Z`

- verdict: `jwst07_smbh_precoces_supported`
- chi2_mbh: `121.83652929640178`
- chi2_lbol: `50.12953473053861`
- chi2_ratio: `32.42312418241683`
- chi2_compactness: `5.377249995189193`
- baseline_total_chi2: `411.23980945821813`
- total_chi2: `209.7664382045464`
- delta_chi2: `201.47337125367173`
- mean_mbh_log_hom: `7.67`
- mean_lbol_log_hom: `46.222`
- mean_ratio_hom: `0.018`
- mean_compactness_hom: `0.754`

## Fichiers produits
- [results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.json](results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.json)
- [results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.txt](results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.txt)
- [results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.csv](results/result-analyse/jwst007_smbh_pipeline/jwst007_smbh_pipeline_20260522-164213Z.csv)

## Conclusion
JWST-07 est retenu comme démonstration calculée pilote pour les SMBH précoces dans le registre V70. Le verdict de la pipeline est `jwst07_smbh_precoces_supported` et le gain global est `delta_chi2=201.47337125367173`.