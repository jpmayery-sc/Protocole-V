# Protocole JWST-03

## But
Valider par une pipeline locale que les tendances de catalogues JWST restent cohérentes après homogénéisation des critères de sélection et du traitement des AGN.

## Pipeline utilisée
Fichier: [python/scripts/runjwst003_catalog_pipeline.py](python/scripts/runjwst003_catalog_pipeline.py)

Principe:
- homogénéisation d un catalogue JWST synthétique;
- comparaison des densités de nombre N(z) et des fractions d AGN f_AGN(z) entre le catalogue homogénéisé et une référence plus biaisée;
- calcul de chi2 séparés pour N(z) et f_AGN(z).

## Résultats mesurés
Exécution: `20260522-153336Z`

- verdict: `jwst03_homogenized_supported`
- chi2_n: `7.515688133707378`
- chi2_agn: `21.19139344852965`
- baseline_chi2_n: `99.03574870739591`
- baseline_chi2_agn: `77.41099343169955`
- delta_chi2: `147.73966055685844`

## Observables homogénéisées
- mean_n_hom: `21.15`
- mean_f_agn: `0.178`

## Interprétation
Le catalogue homogénéisé réduit nettement l écart par rapport à la référence biaisée, avec une amélioration de `147.73966055685844` sur le chi2 total. La correction de pente en redshift améliore maintenant à la fois la densité de nombre et la fraction d AGN, y compris au-delà de `z \gtrsim 2.5`.

## Fichiers produits
- [results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.json](results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.json)
- [results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.txt](results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.txt)
- [results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.csv](results/result-analyse/jwst003_catalog_pipeline/jwst003_catalog_pipeline_20260522-153336Z.csv)

## Conclusion
JWST-03 fournit une démonstration calculée pilote pour les catalogues JWST dans le registre V70. Le cas peut être placé avant JWST-01 comme étape préparatoire du même fil JWST.