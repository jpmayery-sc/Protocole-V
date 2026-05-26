# Protocole PART-03

## But
Vérifier que le modèle géométrique K/T/Y + D1/D2 + Lent reste compatible avec les observables QED ultra-précises liées au rayon de charge du proton, tout en gardant une contribution locale propre nulle.

## Pipeline utilisée
Fichier: [python/scripts/runpart003_proton_radius_neutrality_pipeline.py](python/scripts/runpart003_proton_radius_neutrality_pipeline.py)

Principe:
- imposer un Hamiltonien atomique standard pour l'hydrogène et l'hydrogène muonique;
- comparer des observables non nulles aux niveaux Lamb et aux vertex e-p / mu-p;
- vérifier que le modèle reste plus proche des mesures que le baseline;
- confirmer que la correction locale propre du modèle reste nulle.

## Résultats mesurés
Exécution: `20260522-170428Z`

- verdict: `part03_proton_radius_supported`
- chi2_model: `0.06777777777777776`
- chi2_baseline: `219.93916666666667`
- delta_chi2: `219.87138888888887`
- max_abs_local_shift: `0.0`

## Contrôles locaux
- delta_rp: `0.0`
- lamb_shift_shift: `0.0`
- ep_vertex_shift: `0.0`
- mup_vertex_shift: `0.0`

## Fichiers produits
- [results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.json](results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.json)
- [results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.txt](results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.txt)
- [results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.csv](results/result-analyse/part003_proton_radius_neutrality_pipeline/part003_proton_radius_neutrality_pipeline_20260522-170428Z.csv)

## Conclusion
PART-03 confirme la compatibilité du modèle avec la spectroscopie atomique et avec le rayon de charge du proton. Le verdict de la pipeline est `part03_proton_radius_supported` et le gain global est `delta_chi2=219.87138888888887`.