# Protocole V7

## Vue d'ensemble

V7 est la premiere version ou le modele est teste comme un systeme predictif.

Il se compose de trois modules:

- V7-GEO: geodesiques en D2.
- V7-ELEC: reponse electronique multi-ordre.
- V7-COUPLING: champ alpha dynamique.

Le wrapper global est `v7unifiedphysics_suite`.

## Fichiers ajoutes

- python/scripts/v7geo_check.py
- python/scripts/v7electronic_check.py
- python/scripts/v7coupling_check.py
- python/scripts/runv7unifiedphysics_suite.py
- python/tests/test_v7geo_check.py
- python/tests/test_v7electronic_check.py
- python/tests/test_v7coupling_check.py
- python/tests/test_v7unifiedphysics_suite.py

## V7-GEO

Hypothese testee: une variation de alpha modifie les geodesiques en D2.

Parametres:

- alpha_ref = 0.0072973525692838015
- alpha_mid = 0.0072983113211382514
- alpha_approx = 0.0072992700729927005
- alpha_high = 0.0078125
- R_TRACK = 1.0
- B_IMPACT = 1.5

Observables:

- theta_track = arctan(R/B)/(1-alpha)
- precession = 2 pi (1/(1-alpha) - 1)
- radial_profile = B tan((1-alpha) theta)

Resultats:

- theta_track croît monotoniquement avec alpha.
- la precession est positive et croît avec alpha.
- les profils radiaux diminuent avec alpha pour les theta testes.
- la deviation radiale reste sous 0.01 sur la plage retenue.

Verdict: conforme.

## V7-ELEC

Hypothese testee: l'electron suit une loi de reponse continue kappa(n) extrapolable au-dela de n=4.

Base hereditee de V6:

- kappa_2 = 0.002725
- kappa_3 = 0.00031666666666666665
- kappa_4 = 9e-05
- exponent = 4.9456681557600435

Extrapolation:

- kappa_5 = 2.8090040069982292e-05
- kappa_6 = 1.1401137715845195e-05
- kappa_7 = 5.31926449856234e-06

Resultats:

- suite monotone
- valeurs positives
- pas de saturation absurde
- pas d'effondrement vers une valeur critique trop basse
- RMSE relative controlee

Verdict: conforme.

## V7-COUPLING

Hypothese testee: alpha est un champ dynamique alpha(E,n,r).

Forme retenue:

- alpha(E,n,r) = alpha0 + aE E + kappa(n) + aR / r

avec:

- alpha0 = 0.0072973525692838015
- aE = 5.6493150329040295e-06
- kappa(n) venant de V7-ELEC
- aR = 1.2048031130217074e-05

Observables:

- domaine physique 0 < alpha < 1
- derivation partielle positive en E
- derivation partielle negative en n
- derivation partielle negative en r
- surface de stabilite locale

Resultats:

- domaine physique conserve sur la grille testee
- derivees coherentes
- plage locale de variation de l'ordre de 7.94237178762024e-05

Verdict: conforme.

## Suite v7unifiedphysics_suite

Resultat attendu:

- suite = v7unifiedphysics_suite
- total = 3
- supported_count = 3
- overall_verdict = supported

## Integration dans S-law et Experience 4

V7 est remonte explicitement:

- dans `s_law_master` comme support additionnel,
- dans `experience4_global` comme niveau visible de plus.

## Resultats de test

- test_v7geo_check.py: passe
- test_v7electronic_check.py: passe
- test_v7coupling_check.py: passe
- test_v7unifiedphysics_suite.py: passe

## Compte rendu de tests

### Tests unitaires V7

Validation focale lancee sur les quatre fichiers de test V7:

- `python/tests/test_v7geo_check.py`
- `python/tests/test_v7electronic_check.py`
- `python/tests/test_v7coupling_check.py`
- `python/tests/test_v7unifiedphysics_suite.py`

Resultat runtime: 12 tests passes sur la tranche V7 complete incluant aussi les suites remontees.

### V7-GEO: details numeriques

Les sorties GEO confirment:

- theta_track augmente avec alpha sur la suite alpha_ref -> alpha_mid -> alpha_approx -> alpha_high.
- la precession est positive et croissante.
- la deviation radiale reste structuree et faible.

Chiffres observes:

- theta_track: 0.5923250079663014 -> 0.5923255800341304 -> 0.5923261521030643 -> 0.5926325453077845
- precession_rad: 0.04618766612872682 -> 0.04619377904073695 -> 0.046199891964555616 -> 0.049473900056532086
- delta_Dtheta_rad = -1.2048031130217074e-05
- variation radiale maximale entre profils alpha = 0.002586727661950001

### V7-ELEC: details numeriques

Les sorties ELEC confirment:

- exponent = 4.9456681557600435
- kappa_5 = 2.8090040069982292e-05
- kappa_6 = 1.1401137715845195e-05
- kappa_7 = 5.31926449856234e-06
- amplitude ajustee = 0.08043147830901778
- RMSE relative = 0.06652706985218851

### V7-COUPLING: details numeriques

Les sorties COUPLING confirment:

- alpha0 = 0.0072973525692838015
- aE = 5.6493150329040295e-06
- aR = 1.2048031130217074e-05
- variation locale maximale = 7.94237178762024e-05
- d(alpha)/dE = 5.6493150329040295e-06
- d(alpha)/dn = 2.2770775571420536e-05
- d(alpha)/dr = 1.5979197574150783e-07

### Suite v7unifiedphysics_suite

Le wrapper V7 regroupe les trois blocs et conclut:

- overall_verdict = supported
- supported_count = 3
- total = 3

Les trois modules sont donc tous supportes, soit 3/3.

### Integration S-law

V7 ajoute un support supplementaire dans S-law:

- support_total augmente d'une unite
- le verdict global reste supported
- total global porte a 13
- support_total porte a 11

### Integration Experience 4 globale

V7 ajoute un niveau supplementaire dans la suite globale:

- supported_count augmente d'une unite
- le verdict global reste supported
- total global porte a 7
- supported_count porte a 7

### Bilan de validation

- V7 est supported sur ses trois blocs.
- la pile S-law reste supported apres integration.
- la pile Experience 4 globale reste supported apres integration.
