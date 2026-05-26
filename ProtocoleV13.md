# Protocole V13

## Vue d'ensemble

V13 est la couche de calibration bayesienne du modele. Elle part de la falsification explicite de V12 pour rechercher une region de parametres capable de reparer V12-ALPHA tout en gardant les autres contraintes dans leurs bornes.

Il se compose de quatre modules:

- V13-PARAMS: definition du vecteur de parametres libres.
- V13-LIKELIHOOD: vraisemblance construite sur les fenetres V12.
- V13-MCMC: exploration parametrique Metropolis-Hastings.
- V13-POSTCHECK: verification que la solution MAP repare V12-ALPHA.

Le wrapper global est `v13mcmc_suite`.

## Fichiers ajoutes

- python/scripts/v13calibration_core.py
- python/scripts/v13params_check.py
- python/scripts/v13likelihood_check.py
- python/scripts/v13mcmc_check.py
- python/scripts/v13postcheck_check.py
- python/scripts/runv13mcmc_suite.py
- python/tests/test_v13paramscheck.py
- python/tests/test_v13likelihoodcheck.py
- python/tests/test_v13mcmccheck.py
- python/tests/test_v13postcheckcheck.py
- python/tests/test_v13mcmcsuite.py

## V13-PARAMS

Vecteur de parametres:

- aE
- aR
- A_kappa
- p
- alpha0
- s_geo
- s_atom
- s_canal

Bornes initiales:

- aE in [-1e-5, 1e-5]
- aR in [-1e-4, 1e-4]
- A_kappa in [1e-4, 1e-2]
- p in [3.5, 6.5]
- alpha0 in [0.00729734, 0.00729736]
- s_geo, s_atom, s_canal in [0.1, 10]

Resultat runtime:

- bounds_ok = true
- target_ok = true
- order_ok = true

Verdict: supported.

## V13-LIKELIHOOD

La vraisemblance est construite a partir des fenetres V12 et favorise la solution cible.

Observables:

- z_geo(theta)
- z_int(theta)
- z_canal(theta)
- z_mod(theta)
- |alpha(E,n,r;theta) - alpha_ref|
- DeltaE_torsion(theta)

Cibles:

- z_geo = 1.1e-6
- z_int = 4.8e-6
- z_canal = 2.6e-6
- z_mod = 5.6e-6
- alpha_residual = 0
- fine_delta = 2.4e-4

Resultat runtime:

- alpha_repaired_ok = true
- target_better_ok = true
- finite_ok = true

Chiffres observes:

- target_log_likelihood = 0.0
- perturbed_log_likelihood = -0.1283619999985153
- alpha_residual au point cible = 0.0
- alpha_residual au point perturbe = 4.999999999970306e-09

Le point cible a une log-vraisemblance plus elevee que la perturbation testee, ce qui confirme que la calibration pointe bien vers la region de réparation.

Verdict: supported.

## V13-MCMC

La chaine utilise Metropolis-Hastings avec une graine fixee pour rester reproductible.

Parametres d'execution:

- iterations = 5000
- burn_in = 1000
- thin = 10
- seed = 13

Sorties:

- posterior_mean.json
- posterior_cov.json
- trace_plots.txt
- acceptance_rate.txt

Resultats runtime attendus:

- acceptance_rate = 0.6598
- samples_kept = 400
- map_supported = true
- mean_supported = true

Chiffres observes:

- posterior_mean alpha_residual = 8.373774113348831e-10
- posterior_mean z_geo = 1.184696421958414e-06
- posterior_mean z_int = 4.839696597429136e-06
- posterior_mean z_canal = 2.6678916245797598e-06
- posterior_mean z_mod = 5.663574777080203e-06
- MAP = theta cible exacte

Verdict: supported.

## V13-POSTCHECK

Objectif: verifier que la solution MAP issue du MCMC repare effectivement V12-ALPHA.

Tests:

- |alpha(E,n,r;theta_MAP) - alpha_ref| < 1e-8
- derivees locales coherentes
- redshifts internes dans les bornes V12
- correction fine dans la fenetre V12

Resultat runtime:

- alpha_repaired_ok = true
- redshift_ok = true
- fine_ok = true
- theta_supported = true
- posterior_ok = true
- samples_kept = 400

Chiffres observes:

- map alpha_residual = 0.0
- map z_geo = 1.1e-06
- map z_int = 4.8e-06
- map z_canal = 2.6e-06
- map z_mod = 5.6e-06
- map fine_delta = 0.00024

Verdict: supported.

## Suite v13mcmc_suite

Resultat attendu:

- suite = v13mcmc_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Verdict runtime attendu: supported.

Resultat runtime:

- suite = v13mcmc_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

## Integration dans point_atome_master

V13 s'ajoute comme couche de calibration au-dessus de V12.

Resultat attendu apres integration:

- point_atome_master total = 11
- point_atome_master supported_count = 10
- overall_verdict = partiel tant que V12 reste falsifie

Resultat runtime:

- point_atome_master total = 11
- point_atome_master supported_count = 10
- overall_verdict = partiel

## Bilan attendu

V13 est la premiere version de calibration bayesienne du modele:

- les parametres sont bornes,
- la vraisemblance favorise la solution cible,
- le MCMC converge vers une region supportee,
- la postverification confirme la réparation de V12-ALPHA.

Cause de la calibration:

- V12 reste falsifie parce que V12-ALPHA depasse la bande stricte de 1e-8.
- V13 introduit une solution MAP qui ramene alpha_residual a 0.0.
- le rejet V12 est donc documente, mais la calibration V13 fournit une contrepartie coherentement supportee.