# Rapport complet

## Résumé exécutif

La chaîne de protocoles du projet converge vers une architecture en couches qui passe d’une base atomique élémentaire à une consolidation à 5 paramètres, puis à une phase de métacalibration et enfin à une couche de recherche hiérarchique V20. Le noyau final validé repose sur les paramètres alpha0, s_geo, s_atom, A_kappa et p. V19 reste un point de fragilité localisé, mais la structure globale du pipeline est stable. V20 confirme une cohérence hiérarchique complète et passe en verdict global supporté.

## Synthèse des protocoles markdown

### V4 à V10

Les premiers protocoles construisent la base atomique et les extensions dynamiques du modèle. V4 pose la stabilité nucléaire, V5 introduit la porte alpha dynamique, V6 relie la porte alpha au canal D2 et à l’électron, V7 unifie les prédictions, et V8 à V10 étendent le cadre aux atomes dynamiques, à l’ionisation et aux régimes spectraux.

### V11 à V14

V11 formalise le redshift global via une somme géométrique, atomique et de canal. V12 est le point falsifié de la chaîne. V13 et V14 ramènent le système vers une forme réduite plus compacte et exploitable.

### V15 à V18

V15 verrouille le noyau final avec 5 paramètres. V16 traduit ce noyau en prédictions internes et externes. V17 valide ces prédictions contre des référentiels externes. V18 affine la calibration avec plusieurs profils et conserve le meilleur profil de calibration.

### V19

V19 ajoute une métacalibration globale sur V18. La suite est localement valide, mais la robustesse globale reste borderline. Le point faible identifié est la partie de robustesse globale, alors que la carte et la sensibilité restent supportées.

### V20

V20 introduit une couche de recherche hiérarchique avec trois axes: géométrie, torsion et hiérarchie. Cette couche confirme la cohérence d’ensemble et donne un verdict global supporté.

## Statut validé

### V19

- Verdict global: partiel
- Supportés: 2/4
- Points supportés: map et sensitivity
- Point fragile: robust_global

### V20

- Verdict global: supporté
- Supportés: 4/4
- Points supportés: geo, torsion, hierarchy, verdict
- Structure détectée: cohérente
- Niveau de confiance: haute

## Agrégation master

La suite maître point_atome intègre désormais V20.

- Total: 18 suites
- Supportées: 16
- Verdict global: partiel

Le verdict reste partiel au niveau master parce que V19 reste borderline, mais l’ajout de V20 ne dégrade pas l’agrégation et confirme la stabilité du socle élargi.

## Tests effectués dans cette session

### Suite V20 ciblée

Commande exécutée:

```powershell
python -m pytest tests\test_v20geocheck.py tests\test_v20torsioncheck.py tests\test_v20hierarchycheck.py tests\test_v20verdictcheck.py tests\test_v20researchsuite.py -q
```

Résultat:

- 9 tests passés
- Aucune régression restante sur la tranche V20

### Suite maître point_atome

Commande exécutée:

```powershell
python -m pytest tests\test_point_atome_master_suite.py -q
```

Résultat:

- 2 tests passés
- L’agrégation master reconnaît bien V20

## Artefacts notables

- [python/scripts/v20research_core.py](python/scripts/v20research_core.py)
- [python/scripts/v20geo_check.py](python/scripts/v20geo_check.py)
- [python/scripts/v20torsion_check.py](python/scripts/v20torsion_check.py)
- [python/scripts/v20hierarchy_check.py](python/scripts/v20hierarchy_check.py)
- [python/scripts/v20verdict_check.py](python/scripts/v20verdict_check.py)
- [python/scripts/runv20research_suite.py](python/scripts/runv20research_suite.py)
- [python/scripts/run_point_atome_master_suite.py](python/scripts/run_point_atome_master_suite.py)
- [python/tests/test_v20researchsuite.py](python/tests/test_v20researchsuite.py)
- [python/tests/test_point_atome_master_suite.py](python/tests/test_point_atome_master_suite.py)

## Conclusion

Le pipeline est désormais étendu jusqu’à V20. Le noyau V15-V18 reste cohérent, V19 localise une faiblesse de robustesse globale, et V20 confirme que la couche de recherche finale est supportée. Le prochain travail logique est une extension V21 centrée sur la résolution de la zone borderline de V19.