# Protocole V8

## Vue d'ensemble

V8 est la version ou l'atome devient un objet predictif a partir des blocs V4 a V7.

Il se compose de trois modules:

- V8-RAYON: rayon atomique effectif depuis le champ alpha(E,n,r).
- V8-LEVEL: correction de niveaux via la torsion D2.
- V8-STABILITY: frontiere de stabilite atomique.

Le wrapper global est `v8atomicsuite`.

## Fichiers ajoutes

- python/scripts/v8rayon_check.py
- python/scripts/v8level_check.py
- python/scripts/v8stability_check.py
- python/scripts/runv8atomic_suite.py
- python/tests/test_v8rayon_check.py
- python/tests/test_v8level_check.py
- python/tests/test_v8stability_check.py
- python/tests/test_v8atomic_suite.py

## V8-RAYON

Hypothese testee: le rayon atomique stable correspond a une zone ou le champ alpha(E,n,r) varie peu.

Parametres herites:

- alpha0 = 0.0072973525692838015
- aE = 5.6493150329040295e-06
- amplitude = 0.08043147830901778
- exponent = 4.9456681557600435
- aR = 1.2048031130217074e-05

Cas testes:

- H
- He
- Fe
- Pb

Resultats runtime:

- H: R_eff = 0.54, alpha_span = 6.374619645617766e-06, gradient_min = 4.131697918455786e-05
- He: R_eff = 0.84, alpha_span = 5.7371576810561625e-06, gradient_min = 1.707487405076116e-05
- Fe: R_eff = 1.68, alpha_span = 2.8685788405280813e-06, gradient_min = 4.26871851269029e-06
- Pb: R_eff = 2.52, alpha_span = 1.9123858936856766e-06, gradient_min = 1.8972082278623508e-06

Verdict: conforme.

Lecture:

- l'ordre H < He < Fe est respecte.
- Pb reste plus mou, avec une pente radiale plus faible que Fe.
- la variation alpha reste sous 1.0e-5 sur toutes les fenetres testees.

## V8-LEVEL

Hypothese testee: la torsion D2 et la porte alpha induisent une correction d'energie analogue a une fine structure.

Base heritee de V6:

- delta_phi_ref = 0.0031087512698201886
- alpha_ref = 0.0072973525692838015

Forme operationnelle:

- delta E_torsion = delta_phi * tau(r)
- delta_phi = delta_phi_ref * Z
- tau(r) = alpha_ref / r

Cas testes:

- H
- He
- Fe
- Pb

Resultats runtime:

- H: delta_E = 4.2010470492753026e-05
- He: delta_E = 5.401346206211103e-05
- Fe: delta_E = 0.0003510875034037217
- Pb: delta_E = 0.0007381839815155175

Verdict: conforme.

Lecture:

- H, He et Fe forment une suite croissante nette.
- toutes les amplitudes restent dans la plage 10^-6 a 10^-3 eV.
- Pb reste dans la bande attendue sans casser le critere principal H -> He -> Fe.

## V8-STABILITY

Hypothese testee: la stabilite atomique est controlee par la surface alpha, la variation kappa(n) et la reserve nucleaire.

Forme operationnelle:

- S(Z) = surface de stabilite / variation de kappa(n)
- surface de stabilite = R_eff / alpha_span
- variation de kappa(n) = |kappa(n_low) - kappa(n_high)|
- une reserve nucleaire faible penalise Pb

Resultats runtime:

- H: score = 22503627.086606804
- He: score = 494157243.52791435
- Fe: score = 10347106023.467422
- Pb: score = 6499933318.812766

Verdict: conforme.

Lecture:

- S(H) reste bas.
- He monte nettement.
- Fe devient le maximum.
- Pb redescend sous Fe, donc la limite lourde est bien visible.

## Suite v8atomicsuite

Resultat attendu:

- suite = v8atomicsuite
- total = 3
- supported_count = 3
- overall_verdict = supported

Resultat runtime:

- overall_verdict = supported
- supported_count = 3
- total = 3

## Integration dans point_atome_master

V8 est remonte dans la pile atomique de master comme un niveau supplementaire visible.

Resultat attendu apres integration:

- point_atome_master total = 6
- point_atome_master supported_count = 6
- overall_verdict = supported

## Resultats de test

- test_v8rayon_check.py: passe
- test_v8level_check.py: passe
- test_v8stability_check.py: passe
- test_v8atomic_suite.py: passe
- test_point_atome_master_suite.py: passe

## Compte rendu de tests

### Tests unitaires V8

Validation focale lancee sur les cinq fichiers de test suivants:

- `python/tests/test_v8rayon_check.py`
- `python/tests/test_v8level_check.py`
- `python/tests/test_v8stability_check.py`
- `python/tests/test_v8atomic_suite.py`
- `python/tests/test_point_atome_master_suite.py`

Resultat runtime: 10 tests passes.

### Bilan

- V8-RAYON est conforme sur H, He, Fe et Pb.
- V8-LEVEL est conforme avec une correction croissante de H vers Fe.
- V8-STABILITY est conforme avec Fe maximum et Pb en declin.
- `v8atomicsuite` est supported sur 3/3.
- `point_atome_master` reste supported apres integration de V8.