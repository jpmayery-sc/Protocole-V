# Protocole V14

## Vue d'ensemble

V14 est la couche de reduction parametrique apres la calibration bayesienne V13. L'objectif n'est pas de predire encore davantage, mais de verifier quels parametres sont vraiment necessaires pour conserver la compatibilite V4 -> V13.

Il se compose de quatre modules:

- V14-SENSI: analyse de sensibilite autour du point MAP de V13.
- V14-RANK: classement des parametres a partir de la sensibilite et du posterior V13.
- V14-REDUCE: construction du vecteur reduit.
- V14-RECHECK: verification de la chaine reduite.

Le wrapper global est `v14reduction_suite`.

## Fichiers ajoutes

- python/scripts/v14reduction_core.py
- python/scripts/v14sensi_check.py
- python/scripts/v14rank_check.py
- python/scripts/v14reduce_check.py
- python/scripts/v14recheck_check.py
- python/scripts/runv14reduction_suite.py
- python/tests/test_v14sensicheck.py
- python/tests/test_v14rankcheck.py
- python/tests/test_v14reducecheck.py
- python/tests/test_v14recheckcheck.py
- python/tests/test_v14reductionsuite.py

## V14-SENSI

Hypothese testee: autour du MAP de V13, certains parametres ont un impact faible et peuvent etre figees.

Resultat runtime attendu:

- keep_names = alpha0, s_geo, s_atom, A_kappa, p
- freeze_names = aE, aR, s_canal

Chiffres observes:

- alpha0: rank=1, score=0.020000000006820118
- s_geo: rank=2, score=0.04083333333333252
- s_atom: rank=3, score=0.04083333333333252
- A_kappa: rank=4, score=0.1550000000000001
- p: rank=5, score=0.022499999999999527
- aE: rank=6, score=0.0533333373231971
- aR: rank=7, score=0.03333335336938916
- s_canal: rank=8, score=0.037499999999999645

Lecture:

- alpha0 domine la reparation de V12-ALPHA.
- s_geo et s_atom portent la structure geometrique.
- A_kappa et p restent necessaires pour la partie fine.
- aE, aR et s_canal sont les meilleurs candidats a la reduction.

Verdict: supported.

## V14-RANK

Hypothese testee: le posterior V13 et la sensibilite locale doivent conduire au meme noyau reduit.

Classement attendu:

- fortement contraints: alpha0, s_geo, s_atom
- faiblement contraints: A_kappa, p
- quasi-plats: aE, aR, s_canal

Resultat runtime attendu:

- keep_names = alpha0, s_geo, s_atom, A_kappa, p
- strong = alpha0, s_geo, s_atom
- weak = A_kappa, p
- flat = aE, aR, s_canal

Chiffres observes:

- keep_names = alpha0, s_geo, s_atom, A_kappa, p
- strong = alpha0, s_geo, s_atom
- weak = A_kappa, p
- flat = aE, aR, s_canal

Verdict: supported.

## V14-REDUCE

Vecteur reduit retenu:

- alpha0
- s_geo
- s_atom
- A_kappa
- p

Parametres figes:

- aE
- aR
- s_canal

Ratio de reduction attendu:

- 5 / 8 = 0.625

Lecture:

- la reduction elimine trois parametres quasi-plats sans casser la calibration.
- la solution reduite conserve alpha reparé, redshifts V11 et correction fine V12.

Chiffres observes:

- reduction_ratio = 0.625
- alpha_repaired_ok = true
- redshift_ok = true
- fine_ok = true
- supported = true

Verdict: supported.

## V14-RECHECK

Hypothese testee: le vecteur reduit conserve la compatibilite V11-V13.

Tests:

- V11 reste dans ses fenetres.
- V12 est repare par alpha_residual < 1e-8.
- V13 reste supporte.

Resultat runtime attendu:

- v11_ok = true
- v12_ok = true
- v13_ok = true

Chiffres observes:

- v11_ok = true
- v12_ok = true
- v13_ok = true

Verdict: supported.

## Suite v14reduction_suite

Resultat attendu:

- suite = v14reduction_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

## Integration dans point_atome_master

V14 s'ajoute comme couche de reduction au-dessus de la calibration V13.

Resultat attendu apres integration:

- point_atome_master total = 12
- point_atome_master supported_count = 11
- overall_verdict = partiel

Resultat runtime:

- point_atome_master total = 12
- point_atome_master supported_count = 11
- overall_verdict = partiel

## Bilan attendu

V14 valide une reduction propre du modele:

- trois parametres peuvent etre figees,
- cinq parametres suffisent a conserver la calibration,
- la chaine V11 -> V12 -> V13 reste coherente,
- le modele est maintenant plus compact sans perte fonctionnelle.

Conclusion courte:

- V14 conserve la calibration V13 en gelant aE, aR et s_canal.
- le vecteur reduit retenu est (alpha0, s_geo, s_atom, A_kappa, p).
- la chaîne reste compatible avec V11, V12 et V13.