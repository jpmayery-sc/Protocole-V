# Protocole JWST-06

## But
Tester si la partition AGN / galaxies dans la reionisation peut être stabilisée dans un cadre géométrique K/T/Y + D1/D2, sans hypothèses extrêmes ni mini-quasars spéculatifs.

## Pipeline utilisée
Fichier: [python/scripts/runjwst006_reionisation_agn_pipeline.py](python/scripts/runjwst006_reionisation_agn_pipeline.py)

Principe:
- homogénéiser le catalogue AGN sur la densité d'AGN, la fraction d'échappement et le timing H/He;
- comparer les observables homogénéisées aux prédictions d'un modèle K/T/Y + D1/D2;
- calculer des chi2 séparés pour la densité AGN, fesc_AGN, Q_HII et Q_HeIII.

## Résultats mesurés
Exécution: `20260522-163741Z`

- verdict: `jwst06_reionisation_agn_supported`
- chi2_agn: `0.8240422845952384`
- chi2_fesc: `62.079542041459405`
- chi2_qhii: `38.68246049621183`
- chi2_qheiii: `20.988672501584894`
- baseline_total_chi2: `460.0121237946696`
- total_chi2: `122.57471732385136`
- delta_chi2: `337.43740647081825`
- mean_n_agn_hom: `0.23399999999999999`
- mean_fesc_agn_hom: `0.13`
- mean_q_hii_hom: `0.5860000000000001`
- mean_q_heiii_hom: `0.076`

## Fichiers produits
- [results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.json](results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.json)
- [results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.txt](results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.txt)
- [results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.csv](results/result-analyse/jwst006_reionisation_agn_pipeline/jwst006_reionisation_agn_pipeline_20260522-163741Z.csv)

## Conclusion
JWST-06 est retenu comme démonstration calculée pilote pour la reionisation AGN dans le registre V70. Le verdict de la pipeline est `jwst06_reionisation_agn_supported` et le gain global est `delta_chi2=337.43740647081825`.