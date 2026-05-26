# Protocole V12

## Vue d'ensemble

V12 est la couche de falsification explicite du modele. Elle s'appuie sur les observables construits jusqu'a V11 et les soumet a des bornes conservatrices.

Il se compose de quatre modules:

- V12-ABSOLUTE: bornes absolues sur les redshifts internes.
- V12-ALPHA: bornes sur le champ alpha(E,n,r).
- V12-FINE: bornes sur les corrections fines extrêmes.
- V12-GLOBAL: verdict global de falsification.

Le wrapper global est `v12falsifier_suite`.

## Fichiers ajoutes

- python/scripts/v12absolute_check.py
- python/scripts/v12alpha_check.py
- python/scripts/v12fine_check.py
- python/scripts/v12global_check.py
- python/scripts/runv12falsifiersuite.py
- python/tests/testv12absolutecheck.py
- python/tests/testv12alphacheck.py
- python/tests/testv12finecheck.py
- python/tests/testv12globalcheck.py
- python/tests/testv12falsifiersuite.py

## V12-ABSOLUTE

Hypothese testee: les redshifts internes de V11 doivent rester dans des bornes conservatrices.

Bornes appliquees:

- V11-GEO: 10^-7 a 2 x 10^-6
- V11-ATOM: 10^-7 a 10^-5
- V11-CANAL: 5 x 10^-7 a 5 x 10^-6
- V11-TOTAL: 10^-6 a 10^-5

Resultats runtime:

- geo nominal: 2.4393147611216526e-07, 3.679131767807885e-07, 6.362881995694561e-07, 7.479221292365444e-07
- atom nominal: 3.9354070719206714e-07, 5.747095007535248e-07, 3.3521805572804293e-06, 5.854048846888991e-06, 6.115808664454451e-06
- canal nominal: 8.98645350096726e-07, 1.1040267160788616e-06, 2.0923048556515816e-06, 2.4717661281133484e-06
- total nominal: 1.5361175334009585e-06, 2.0466493936131747e-06, 6.080773612501467e-06, 9.073737104238884e-06

Verdict: conforme.

Lecture:

- toutes les valeurs nominales restent dans les bornes.
- la progression reste ordonnee.

## V12-ALPHA

Hypothese testee: le champ alpha(E,n,r) doit rester proche de la valeur de reference et garder une structure coherente.

Bornes appliquees:

- |alpha(E,n,r) - alpha_ref| <= 10^-8
- derivee radiale non renversee
- surface de stabilite non nulle

Resultats runtime:

- alpha_ref = 0.0072973525692838015
- max |alpha - alpha_ref| = 3.4181437466225886e-04
- stability_range = 8.026792849464594e-05

Verdict: falsifie.

Lecture:

- la bande stricte est largement depassee: l'ecart maximal vaut 3.4181437466225886e-04 alors que la tolérance imposee est 1e-8.
- la structure radiale reste coherente, mais cela ne compense pas l'echec de la contrainte absolue sur alpha.
- ce bloc falsifie donc V12 a lui seul, meme si les derivees locales restent compatibles.

Pourquoi ce bloc est falsifie:

- la condition la plus discriminante est la proximite a alpha_ref.
- ici, le domaine autorise est de 1e-8, tandis que l'ecart observe est plus de 34 000 fois plus grand.
- le bloc n'est donc pas seulement "limite" ou "partiel": il contredit la contrainte principale.

## V12-FINE

Hypothese testee: les corrections fines doivent rester dans une plage realiste et garder la hiérarchie avec Z.

Cas testes:

- H
- He
- Fe
- Xe
- Pb
- U

Resultats runtime:

- H: correction = 9.924973653912903e-06
- He: correction = 1.9849947307825806e-05
- Fe: correction = 1.1468858444521576e-04
- Xe: correction = 2.385187911215631e-04
- Pb: correction = 3.646990828394342e-04
- U: correction = 4.242438934559944e-04

Verdict: conforme.

Lecture:

- les amplitudes restent entre 10^-6 et 10^-3 eV.
- la montée avec Z est nette.
- Fe reste en zone stable.

## V12-GLOBAL

Hypothese testee: le modele est rejete si un bloc V12 est falsifie.

Règle:

- supported si tous les blocs sont conformes
- partial si aucun bloc n'est falsifie mais qu'un bloc est limite
- falsified si au moins un bloc est clairement hors bornes

Resultat runtime:

- supported_count = 2
- partial_count = 0
- falsified_count = 1
- overall_verdict = falsified

Verdict: falsifie.

Lecture:

- V12-ABSOLUTE et V12-FINE passent.
- V12-ALPHA echoue sur la bande stricte.
- V12-GLOBAL tranche donc en rejet explicite.

Pourquoi le global est falsifie:

- le bloc V12-ALPHA est le seul bloc en echec, mais il suffit a invalider la suite.
- les blocs conformes ne compensent pas une falsification nette sur une contrainte centrale.
- le verdict global ne peut donc pas etre "supported" ni "partiel": il doit etre "falsified".

## Suite v12falsifier_suite

Resultat attendu:

- suite = v12falsifier_suite
- total = 4
- supported_count = 2
- overall_verdict = falsified

Resultat runtime:

- overall_verdict = falsified
- supported_count = 2
- total = 4

## Integration dans point_atome_master

V12 remonte dans la pile atomique comme couche de falsification explicite.

Resultat attendu apres integration:

- point_atome_master total = 10
- point_atome_master supported_count = 9
- overall_verdict = partiel

## Resultats de test

- test_v12absolutecheck.py: passe
- test_v12alphacheck.py: passe
- test_v12finecheck.py: passe
- test_v12globalcheck.py: passe
- test_v12falsifiersuite.py: passe
- test_point_atome_master_suite.py: passe

## Compte rendu de tests

### Tests unitaires V12

Validation focale lancee sur les six fichiers de test suivants:

- `python/tests/test_v12absolutecheck.py`
- `python/tests/test_v12alphacheck.py`
- `python/tests/test_v12finecheck.py`
- `python/tests/test_v12globalcheck.py`
- `python/tests/test_v12falsifiersuite.py`
- `python/tests/test_point_atome_master_suite.py`

Resultat runtime: 12 tests passes.

### Bilan

- V12-ABSOLUTE passe les bornes conservatrices.
- V12-ALPHA est falsifie par la bande stricte.
- V12-FINE reste conforme.
- `v12falsifier_suite` conclut a `falsified`.
- `point_atome_master` devient `partiel` apres ajout de V12.

Conclusion courte:

- V12 est falsifie parce que le champ alpha(E,n,r) s'ecarte trop de sa reference.
- l'ecart observe est 3.4181437466225886e-04, tres au-dessus de la bande autorisee de 1e-8.
- la falsification est donc motivee par une contradiction quantitative, pas par une simple irregularite de forme.