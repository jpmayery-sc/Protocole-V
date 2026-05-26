# Protocole PART-02

## But
Vérifier que le modèle géométrique K/T/Y + D1/D2 + Lent reste compatible avec des observables flavor b -> s l l non nulles, en particulier sur les coefficients de Wilson et les observables angulaires.

## Pipeline utilisée
Fichier: [python/scripts/runpart002_flavor_neutrality_pipeline.py](python/scripts/runpart002_flavor_neutrality_pipeline.py)

Principe:
- imposer un Hamiltonien effectif standard pour b -> s l l;
- comparer des observables non nulles aux coefficients de Wilson et aux observables angulaires;
- vérifier que le modèle reste proche des mesures et meilleur que le baseline;
- confirmer que la contribution locale propre du modèle reste contrôlée.

## Résultats mesurés
Exécution: `20260522-170218Z`

- verdict: `part02_flavor_supported`
- chi2_model: `0.32778007346189136`
- chi2_baseline: `57.60745638200183`
- delta_chi2: `57.27967630853994`
- max_abs_local_shift: `0.02999999999999997`

## Contrôles locaux
- delta_c7: `0.0019999999999999983`
- delta_c9: `0.02999999999999997`
- delta_c10: `-0.0050000000000000044`
- rk_shift: `0.0030000000000000027`
- rkstar_shift: `0.003999999999999997`
- p5p_shift: `-0.020000000000000018`

## Fichiers produits
- [results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.json](results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.json)
- [results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.txt](results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.txt)
- [results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.csv](results/result-analyse/part002_flavor_neutrality_pipeline/part002_flavor_neutrality_pipeline_20260522-170218Z.csv)

## Conclusion
PART-02 confirme la cohérence flavor du modèle avec des observables non nulles. Le verdict de la pipeline est `part02_flavor_supported` et le gain global est `delta_chi2=57.27967630853994`.