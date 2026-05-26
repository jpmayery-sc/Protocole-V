# Protocole JWST-05

## But
Tester si la crise photonique de reionisation peut être réduite par une homogénéisation cohérente des hypothèses et par une topologie D1/D2 du cocon, sans invoquer de rupture cosmologique ni de population exotique.

## Pipeline utilisée
Fichier: [python/scripts/runjwst005_reionisation_pipeline.py](python/scripts/runjwst005_reionisation_pipeline.py)

Principe:
- homogénéiser le catalogue sur le rendement ionisant, la fraction d'échappement et l'abondance à z > 9;
- comparer les observables homogénéisées aux prédictions d'un modèle K/T/Y + D1/D2;
- calculer des chi2 séparés pour xiion, fesc, n(z > 9) et tau.

## Résultats attendus
- xiion modéré par la compacité géométrique;
- fesc augmenté par des canaux anisotropes;
- abondance z > 9 relue via l'efficacité baryonique;
- tau compatible avec le CMB.

## Résultats mesurés
Exécution: `20260522-163449Z`

- verdict: `jwst05_reionisation_supported`
- chi2_xiion: `3.4308148997353234`
- chi2_fesc: `17.66746892986548`
- chi2_n: `4.28688363552658`
- chi2_tau: `3.910506250000007`
- baseline_total_chi2: `498.3863247935288`
- total_chi2: `29.29567371512739`
- delta_chi2: `469.0906510784014`
- mean_xiion_hom: `25.145999999999997`
- mean_fesc_hom: `0.0836`
- mean_n_hom: `0.40599999999999997`
- tau_hom: `0.056`

## Fichiers produits
- [results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.json](results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.json)
- [results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.txt](results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.txt)
- [results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.csv](results/result-analyse/jwst005_reionisation_pipeline/jwst005_reionisation_pipeline_20260522-163449Z.csv)

## Conclusion
JWST-05 est retenu comme démonstration calculée pilote pour la reionisation dans le registre V70. Le verdict de la pipeline est `jwst05_reionisation_supported` et le gain global est `delta_chi2=469.0906510784014`.