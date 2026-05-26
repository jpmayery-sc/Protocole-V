# Protocole V17

## Vue d'ensemble

V17 est la couche de validation externe du modele V16. L'objectif est de confronter les predictions de V16 a un referentiel externe minimal, puis de classer la compatibilite en supported, marginal ou falsified.

Il se compose de quatre modules:

- V17-REFERENCE: chargement du referentiel externe.
- V17-COMPARE: comparaison V16 versus reference.
- V17-DEVIATION: analyse des ecarts.
- V17-VERDICT: decision finale.

Le wrapper global est `v17validation_suite`.

## Fichiers ajoutes

- python/scripts/v17validation_core.py
- python/scripts/v17reference_check.py
- python/scripts/v17compare_check.py
- python/scripts/v17deviation_check.py
- python/scripts/v17verdict_check.py
- python/scripts/runv17validation_suite.py
- python/tests/test_v17referencecheck.py
- python/tests/test_v17comparecheck.py
- python/tests/test_v17deviationcheck.py
- python/tests/test_v17verdictcheck.py
- python/tests/test_v17validationsuite.py

## V17-REFERENCE

Hypothese testee: un referentiel externe minimal peut servir de base de validation pour V16.

Referentiel retenu:

- source = minimal theoretical bounds
- locked_names = alpha0, s_geo, s_atom, A_kappa, p
- frozen_names = aE, aR, s_canal

Bornes et cibles de reference:

- z_obs: target = 0.000125, bounds = [0.0001, 0.00015]
- delta_nu_over_nu: target = 2.85e-05, bounds = [2.5e-05, 3.5e-05]
- delta_E: target = 2.4e-05, bounds = [2.0e-05, 2.8e-05]
- fine_correction_eff: target = 2.0, bounds = [1.5, 2.5]
- grav_torsion_eff: target = -0.00012, bounds = [-0.0002, 0.0]

Verdict: supported.

## V17-COMPARE

Hypothese testee: V16 reste dans les bornes de reference externes.

Resultat runtime:

- all_in_bounds = true
- all_signs_ok = true
- comparison_ok = true

Comparaisons observees:

- z_obs: predicted = 0.0001256, target = 0.000125, absolute_error = 5.999999999999875e-07, relative_error = 0.0047999999999999, center_offset = 0.023999999999999508
- delta_nu_over_nu: predicted = 2.96e-05, target = 2.85e-05, absolute_error = 1.0999999999999996e-06, relative_error = 0.038596491228070164, center_offset = 0.07999999999999927
- delta_E: predicted = 2.40056e-05, target = 2.4e-05, absolute_error = 5.599999999998727e-09, relative_error = 0.00023333333333328026, center_offset = 0.001399999999999682
- fine_correction_eff: predicted = 2.0, target = 2.0, absolute_error = 0.0, relative_error = 0.0, center_offset = 0.0
- grav_torsion_eff: predicted = -0.00011999999999999999, target = -0.00012, absolute_error = 1.3552527156068805e-20, relative_error = 1.1293772630057339e-16, center_offset = 0.19999999999999984

Verdict: supported.

## V17-DEVIATION

Hypothese testee: les ecarts V16/reference restent faibles.

Resultat runtime:

- deviation_score = 0.061079999999999655
- deviation_class = supported
- monotone_ok = true

Deviation vector observe:

- z_obs = 0.023999999999999508
- delta_nu_over_nu = 0.07999999999999927
- delta_E = 0.001399999999999682
- fine_correction_eff = 0.0
- grav_torsion_eff = 0.19999999999999984

Lecture:

- les ecarts sont faibles et restent bien en dessous du seuil de marginalite.
- le classement reste supporte par les bornes et les signes.

Verdict: supported.

## V17-VERDICT

Hypothese testee: V16 reste compatible, marginal ou incompatible face au referentiel externe.

Resultat runtime:

- verdict = supported
- locked_names = alpha0, s_geo, s_atom, A_kappa, p
- frozen_names = aE, aR, s_canal

Verdict final: supported.

## Suite v17validation_suite

Resultat runtime:

- suite = v17validation_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Items:

- v17_reference: supported
- v17_compare: supported
- v17_deviation: supported
- v17_verdict: supported

## Integration dans point_atome_master

V17 s'ajoute comme couche de validation externe au-dessus de V16.

Resultat runtime:

- point_atome_master total = 15
- point_atome_master supported_count = 14
- overall_verdict = partiel

Lecture:

- V11, V13, V14, V15, V16 et V17 sont supportees.
- V12 reste falsifiee, donc le master global demeure partiel.

## Bilan attendu

V17 valide V16 contre un referentiel externe minimal:

- les comparaisons restent dans les bornes,
- la deviation globale reste faible,
- le verdict final est supported.

Conclusion courte:

- V17 confirme que V16 est compatible avec un referentiel externe minimal.
- V17 est supporte en 4/4.
- le modele peut maintenant servir de base a une calibration externe plus fine.