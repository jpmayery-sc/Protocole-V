# Protocole UHECR-01

## But
Vérifier que le modèle géométrique K/T/Y + D1/D2 + Lent reste compatible avec l'anisotropie dipolaire des rayons cosmiques ultra-énergétiques au-delà de 8 EeV, sans modifier la propagation des particules ni les champs magnétiques.

## Pipeline utilisée
Fichier: [python/scripts/runuhecr001_propagation_pipeline.py](python/scripts/runuhecr001_propagation_pipeline.py)

Principe:
- imposer la propagation UHECR standard dans les champs magnétiques galactiques et extragalactiques;
- comparer des observables non nulles pour l'amplitude dipolaire, la direction du dipôle, la distribution angulaire et la cohérence avec les catalogues de galaxies;
- vérifier que le modèle reste plus proche des mesures que le baseline;
- confirmer qu'aucune correction locale de propagation n'est introduite par le modèle.

## Résultats mesurés
Exécution: `20260522-170744Z`

- verdict: `uhecr01_propagation_supported`
- chi2_model: `0.12777777777777785`
- chi2_baseline: `63.25`
- delta_chi2: `63.12222222222222`
- max_abs_local_shift: `0.0`

## Contrôles locaux
- dipole_amplitude_shift: `0.0`
- dipole_direction_shift: `0.0`
- large_scale_distribution_shift: `0.0`
- catalog_coherence_shift: `0.0`

## Fichiers produits
- [results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.json](results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.json)
- [results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.txt](results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.txt)
- [results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.csv](results/result-analyse/uhecr001_propagation_pipeline/uhecr001_propagation_pipeline_20260522-170744Z.csv)

## Conclusion
UHECR-01 confirme la compatibilité du modèle avec l'anisotropie dipolaire observée des UHECR tout en conservant des contrôles locaux nuls. Le verdict de la pipeline est `uhecr01_propagation_supported` et le gain global est `delta_chi2=63.12222222222222`.