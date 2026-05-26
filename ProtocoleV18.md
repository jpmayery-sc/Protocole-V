# Protocole V18

## Vue d'ensemble

V18 est la couche de calibration externe fine du modele issu de V17. L'objectif est de tester trois profils de calibration sur le noyau V15/V16/V17, puis de retenir le meilleur profil sans casser la stabilite ni la compatibilite externe.

Il se compose de quatre modules:

- V18-DELTA: calcul du delta de reference depuis V17.
- V18-CALIBRATE: comparaison des trois profils de calibration.
- V18-RECHECK: verification du meilleur profil retenu.
- V18-VERDICT: decision finale V18.

Le wrapper global est `v18calibration_suite`.

## Fichiers ajoutes

- python/scripts/v18calibration_core.py
- python/scripts/v18delta_check.py
- python/scripts/v18calibrate_check.py
- python/scripts/v18recheck_check.py
- python/scripts/v18verdict_check.py
- python/scripts/runv18calibration_suite.py
- python/tests/test_v18deltacheck.py
- python/tests/test_v18calibratecheck.py
- python/tests/test_v18recheckcheck.py
- python/tests/test_v18verdictcheck.py
- python/tests/test_v18calibrationsuite.py

## V18-DELTA

Hypothese testee: V17 fournit un delta utile pour calibrer finement V18.

Reference de depart:

- deviation_score = 0.061079999999999655
- deviation_class = supported

Comparaison observee:

- z_obs = 0.0001256
- delta_nu_over_nu = 2.96e-05
- delta_E = 2.40056e-05
- fine_correction_eff = 2.0
- grav_torsion_eff = -0.00011999999999999999

Lecture:

- le delta V17 reste supporte.
- les bornes externes restent compatibles.
- la base V18 peut donc partir du noyau V17 sans rupture.

Verdict: supported.

## V18-CALIBRATE

Hypothese testee: trois calibrations fines peuvent reduire les ecarts sans casser la stabilite V15/V16/V17.

Profils testes:

- calibration_douce
- calibration_standard
- calibration_agressive

Resultat runtime:

- profile_count = 3
- supported_profiles = 3
- best_profile = calibration_agressive
- baseline_deviation_score = 0.061079999999999655
- best_deviation_score = 0.06098758233333329
- improved = true
- neutral = false

Meilleur profil retenu:

- aE = 0.0
- aR = 0.0
- A_kappa = 0.001002
- p = 5.01
- alpha0 = 0.0072973525692838015
- s_geo = 0.999
- s_atom = 0.999
- s_canal = 1.0

Sorties V16 induites par le meilleur profil:

- z_obs = 0.00012559018
- delta_nu_over_nu = 2.9598180000000003e-05
- delta_E = 2.4003600180000002e-05
- fine_correction_eff = 1.9999166666666666
- grav_torsion_eff = -0.00011999000000000001

Comparaison qualitative:

- internal_ok = true
- external_ok = true
- comparison_ok = true

Lecture:

- le meilleur profil reste supporte.
- le score de deviation baisse par rapport au baseline V17.
- la calibration agressive devient le meilleur compromis observe.

Verdict: supported-improved.

## V18-RECHECK

Hypothese testee: la meilleure calibration V18 conserve V16/V17 et reduit le delta.

Resultat runtime:

- best_profile = calibration_agressive
- baseline_deviation_score = 0.061079999999999655
- best_deviation_score = 0.06098758233333329
- improved = true
- internal_ok = true
- external_ok = true
- comparison_ok = true

Lecture:

- le profil retenu reste dans les bornes.
- le meilleur score est strictement meilleur que le baseline.
- la compatibilite structurelle reste intacte.

Verdict: supported.

## V18-VERDICT

Hypothese testee: V18 peut ameliorer la calibration externe sans casser V15/V16/V17.

Resultat runtime:

- verdict = supported-improved
- best_profile = calibration_agressive
- baseline_deviation_score = 0.061079999999999655
- best_deviation_score = 0.06098758233333329

Verdict final: supported-improved.

## Suite v18calibration_suite

Resultat runtime:

- suite = v18calibration_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Items:

- v18_delta: supported
- v18_calibrate: supported-improved
- v18_recheck: supported
- v18_verdict: supported-improved

## Integration dans point_atome_master

V18 s'ajoute comme couche de calibration externe fine au-dessus de V17.

Resultat runtime:

- point_atome_master total = 16
- point_atome_master supported_count = 15
- overall_verdict = partiel

Lecture:

- V11, V13, V14, V15, V16, V17 et V18 sont supportees.
- V12 reste falsifiee, donc le master global demeure partiel.

## Bilan attendu

V18 confirme qu'une calibration externe fine peut encore reduire l'ecart global:

- trois profils ont ete testes,
- tous les profils sont restes supportes,
- le meilleur profil est calibration_agressive,
- le score de deviation est abaisse sans casser la structure precedente.

Conclusion courte:

- V18 ameliore la calibration externe du modele.
- V18 est supporte en 4/4.
- le meilleur profil retenu est calibration_agressive.
