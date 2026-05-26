# Protocole TRANS-01

## But
Vérifier que le modèle géométrique K/T/Y + D1/D2 + Lent reste cohérent avec la distribution baryonique déduite des FRB, tout en produisant des observables DM(z) non nulles et une amélioration nette par rapport au baseline.

## Pipeline utilisée
Fichier: [python/scripts/runtrans001_frb_neutrality_pipeline.py](python/scripts/runtrans001_frb_neutrality_pipeline.py)

Principe:
- imposer une propagation radio standard;
- comparer des observables FRB non nulles sur DM(z), sigma_DM, DM×LSS et Omega_b;
- vérifier que le modèle reste proche des données alors que le baseline s'en écarte davantage;
- quantifier les shifts locaux et le gain global.

## Résultats mesurés
Exécution: `20260522-165904Z`

- verdict: `trans01_frb_supported`
- chi2_model: `0.5594135802469146`
- chi2_baseline: `111.1520061728395`
- delta_chi2: `110.5925925925926`
- max_abs_local_shift: `8.0`

## Contrôles locaux
- delta_dm: `-8.0`
- sigma_dm_shift: `0.6000000000000014`
- dm_lss_shift: `-0.0050000000000000044`
- omega_b_shift: `-0.0005000000000000004`

## Fichiers produits
- [results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.json](results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.json)
- [results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.txt](results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.txt)
- [results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.csv](results/result-analyse/trans001_frb_neutrality_pipeline/trans001_frb_neutrality_pipeline_20260522-165904Z.csv)

## Conclusion
TRANS-01 confirme la cohérence baryonique du modèle sur les FRB avec des observables non nulles. Le verdict de la pipeline est `trans01_frb_supported` et le gain global est `delta_chi2=110.5925925925926`.