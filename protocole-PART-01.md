# Protocole PART-01

## But
Vérifier que le modèle géométrique K/T/Y + D1/D2 + Lent reste compatible avec la mesure de g-2 du muon, sans contribution locale au vertex électromagnétique, sans modification du propagateur photonique et sans contamination hadronique.

## Pipeline utilisée
Fichier: [python/scripts/runpart001_g2_neutrality_pipeline.py](python/scripts/runpart001_g2_neutrality_pipeline.py)

Principe:
- imposer un cadre QED local standard pour le muon;
- comparer une valeur de référence non nulle pour $a_\mu$ avec le modèle;
- vérifier qu'aucun terme additionnel n'apparaît au niveau du vertex ou du propagateur;
- mesurer le gain du modèle par rapport à un baseline plus éloigné.

## Résultats mesurés
Exécution: `20260522-170046Z`

- verdict: `part01_g2_supported`
- chi2_model: `0.02777777777777736`
- chi2_baseline: `102.25111111111109`
- delta_chi2: `102.22333333333331`
- max_abs_local_shift: `0.0`

## Contrôles locaux
- vertex_mu_gamma: `0.0`
- photon_propagator_shift: `0.0`
- hadronic_vertex_shift: `0.0`
- lent_qed_coupling: `0.0`

## Fichiers produits
- [results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.json](results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.json)
- [results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.txt](results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.txt)
- [results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.csv](results/result-analyse/part001_g2_neutrality_pipeline/part001_g2_neutrality_pipeline_20260522-170046Z.csv)

## Conclusion
PART-01 confirme la compatibilité du modèle avec g-2 du muon tout en gardant une neutralité locale QED. Le verdict de la pipeline est `part01_g2_supported` et le gain global est `delta_chi2=102.22333333333331`.