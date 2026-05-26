# Protocole V15

## Vue d'ensemble

V15 est la couche de consolidation finale du modele reduit issu de V14. L'objectif n'est plus de reduire davantage, mais de verrouiller le noyau final avant toute prediction.

Il se compose de trois modules:

- V15-STABILITY: test de stabilite sous perturbations.
- V15-ROBUSTNESS: test de robustesse structurelle.
- V15-LOCK: gel final du vecteur reduit.

Le wrapper global est `v15consolidation_suite`.

## Fichiers ajoutes

- python/scripts/v15consolidation_core.py
- python/scripts/v15stability_check.py
- python/scripts/v15robustness_check.py
- python/scripts/v15lock_check.py
- python/scripts/runv15consolidation_suite.py
- python/tests/test_v15stabilitycheck.py
- python/tests/test_v15robustnesscheck.py
- python/tests/test_v15lockcheck.py
- python/tests/test_v15consolidationsuite.py

## V15-STABILITY

Hypothese testee: le modele reduit reste stable sous de petites perturbations des 5 parametres verrouilles.

Regle de test:

- variations de 1%, 5% et 10%
- alpha0 est perturbe sur une echelle de bruit de calibration compatible avec sa tolerance, afin de tester la stabilite sans casser la fenetre alpha

Resultat runtime:

- locked_names = alpha0, s_geo, s_atom, A_kappa, p
- frozen_names = aE, aR, s_canal
- perturbation_levels = 0.01, 0.05, 0.1
- supported_cases = 15 / 15

Lecture:

- toutes les perturbations testees restent supportees
- alpha_residual reste dans la bande autorisee
- les redshifts et la correction fine restent stables

Verdict: supported.

## V15-ROBUSTNESS

Hypothese testee: la structure reduite preserve la coherence des redshifts, du champ alpha et du canal kappa.

Resultat runtime:

- locked_names = alpha0, s_geo, s_atom, A_kappa, p
- frozen_names = aE, aR, s_canal
- supported_rows = 5 / 5

Synthese des tendances observees:

- alpha0: alpha_residual est symetrique et croissant avec l'ecart absolu
- s_geo: z_geo et z_mod sont croissants
- s_atom: z_int et z_mod sont croissants
- A_kappa: z_canal et fine_delta sont croissants
- p: z_mod est croissant et fine_delta est decroissant

Verdict: supported.

## V15-LOCK

Vecteur final verrouille:

- alpha0
- s_geo
- s_atom
- A_kappa
- p

Parametres figes:

- aE
- aR
- s_canal

Vecteur reduit final:

- alpha0 = 0.0072973525692838015
- s_geo = 1.0
- s_atom = 1.0
- A_kappa = 0.001
- p = 5.0

Resultat runtime:

- supported = true
- alpha_repaired_ok = true
- redshift_ok = true
- fine_ok = true

Verdict: supported.

## Suite v15consolidation_suite

Resultat runtime:

- suite = v15consolidation_suite
- total = 3
- supported_count = 3
- overall_verdict = supported

## Integration dans point_atome_master

V15 s'ajoute comme couche de consolidation finale au-dessus de V14.

Resultat runtime:

- point_atome_master total = 13
- point_atome_master supported_count = 12
- overall_verdict = partiel

Lecture:

- V11, V13, V14 et V15 restent supportees
- V12 reste falsifiee, donc le master global demeure partiel

## Bilan attendu

V15 ne change pas la physique validee par V14; il verrouille simplement le noyau final avant la prediction.

Conclusion courte:

- V15 confirme la stabilite du modele reduit.
- V15 confirme la robustesse structurelle du noyau final.
- V15 fige le vecteur (alpha0, s_geo, s_atom, A_kappa, p).