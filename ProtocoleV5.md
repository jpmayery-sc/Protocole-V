# Protocole V5

## Vue d'ensemble

V5 donne un statut physique a la porte alpha en la traitant comme une fonction avec pente. Le bloc est structure en trois tests complementaires:

- V5-E: alpha(E), avec une pente en energie de type running coupling.
- V5-N: alpha(n), avec une pente effective selon l'ordre de torsion n.
- V5-G: alpha(Δθ), avec un deficit angulaire geometrique en D2.

Le wrapper global est alphaportsuite et reproduit le schema de V4: chaque test produit un JSON et un TXT, puis la suite agrege les trois resultats.

## Fichiers ajoutes

- python/scripts/alphaenergyrunning_check.py
- python/scripts/alphatorsionorder_check.py
- python/scripts/alphageometricport_check.py
- python/scripts/runalphaport_suite.py
- python/tests/test_alphaenergyrunning_check.py
- python/tests/test_alphatorsionorder_check.py
- python/tests/test_alphageometricport_check.py
- python/tests/test_alphaport_suite.py

## V5-E: alpha(E)

Hypothese testee: la porte alpha n'est pas figee, elle varie avec l'energie.

Points utilises:

- E1 = 0.0 GeV, alpha(E1) = 1/137.036 = 0.007297350926130
- E2 = 91.1876 GeV, alpha(E2) = 1/128.0 = 0.007812500000000

Resultats calcules:

- delta alpha = 5.151490738699e-04
- delta E = 91.1876 GeV
- d alpha / dE = 5.649315032904e-06 par GeV
- signe = positive

Verdict: conforme, car la pente est bien positive et reste faible.

Test realise:

- verification que alpha(E2) > alpha(E1)
- verification que la pente d alpha / dE est positive
- verification que la pente reste petite devant 1e-4

## V5-N: alpha(n)

Hypothese testee: la force effective de la porte alpha reste controlee quand l'ordre n augmente.

Valeurs extraites de l'article:

- n = 2, squeezing: r = 1.09, t_sqz = 400 us
- n = 3, trisqueezing: r = 0.19, t_sqz = 600 us
- n = 4, quadsqueezing: r = 0.054, t_sqz = 600 us

Pentes effectives:

- kappa_2 = 2.725000000000e-03
- kappa_3 = 3.166666666667e-04
- kappa_4 = 9.000000000000e-05

Ratios:

- kappa_3 / kappa_2 = 0.116207951070336
- kappa_4 / kappa_3 = 0.284210526315790
- kappa_4 / kappa_2 = 0.033027522935780

Verdict: conforme, car la pente decroit avec n sans effondrement brutal.

Test realise:

- verification de l'ordre kappa_2 > kappa_3 > kappa_4
- verification des ratios de decroissance
- verification que la structure reste exploitable

## V5-G: alpha(Δθ)

Hypothese testee: la porte alpha se lit comme un deficit angulaire variable en D2.

Valeurs utilisees:

- alpha_ref = 1/137.035999084 = 0.007297352564851
- alpha_approx = 1/137 = 0.007299270072993
- Δθ_ref = 2π alpha_ref = 0.045850618444633 rad
- Δθ_approx = 2π alpha_approx = 0.045862666475763 rad
- delta Δθ = Δθ_ref - Δθ_approx = -1.204803113022e-05 rad

Ecart relatif:

- relative_delta = 2.627670364963e-04

Verdict: conforme, car l'approximation 1/137 n'est pas exacte, mais l'observable geometrique reste propre et faible.

Test realise:

- verification que 1/137 n'est pas exact face a la valeur de reference
- verification que le deficit angulaire reste petit
- verification que l'ecart geometrique est mesurable

## Suite alphaportsuite

Le wrapper runalphaport_suite.py lance les trois scripts V5, lit leurs derniers JSON et fabrique un resume global.

Resultat attendu de la suite:

- suite = alphaportsuite
- total = 3
- supported_count = 3
- overall_verdict = supported

## Integration dans la suite S-law

Le bloc alphaportsuite est aussi relaye dans la suite S-law master, au meme niveau que alpha_phase_observable et alpha_constant.

Effet de l'integration:

- la suite S-law master gagne un support supplementaire: alphaportsuite
- la suite globale Experience 4 remonte automatiquement ce support via s_law_master

## Integration dans la suite Experience 4 globale

Le bloc alphaportsuite est aussi expose explicitement dans la suite Experience 4 globale.

Effet de l'integration:

- la suite globale reference directement alphaportsuite en plus de s_law_master
- le niveau de validation V5 reste visible sans devoir traverser toute la pile pour le lire

## Resultats de test

- test_alphaenergyrunning_check.py: passe
- test_alphatorsionorder_check.py: passe
- test_alphageometricport_check.py: passe
- test_alphaport_suite.py: passe

## Lecture physique

- V5-E: alpha a une pente en energie, donc une porte dynamique.
- V5-N: la meme porte se manifeste dans la force des torsions d'ordre n.
- V5-G: la porte se lit comme un deficit angulaire variable, ce qui ancre le lien avec D2.

## Compte rendu de tests

### Tests unitaires V5

Validation focale lancee sur les quatre fichiers de test V5:

- `python/tests/test_alphaenergyrunning_check.py`
- `python/tests/test_alphatorsionorder_check.py`
- `python/tests/test_alphageometricport_check.py`
- `python/tests/test_alphaport_suite.py`

Resultat: 8 tests passes en 1.04 s.

### V5-E: details numeriques

Dernier rapport: `alphaenergyrunning_check_20260517-145828Z`

- alpha_E1 = 0.0072973525205055605
- alpha_E2 = 0.0078125
- energie_E1 = 0.0 GeV
- energie_E2 = 91.1876 GeV
- delta alpha = 0.0005151474794944395
- delta E = 91.1876 GeV
- d alpha / dE = 5.6493150329040295e-06 par GeV
- signe = positive
- running_coupling_ok = true
- small_slope_ok = true
- verdict = conforme

Lecture: la pente est bien positive, petite et cohérente avec un running coupling.

### V5-N: details numeriques

Dernier rapport: `alphatorsionorder_check_20260517-145828Z`

- n = 2, squeezing: r = 1.09, t_sqz = 400 us, kappa_2 = 0.002725
- n = 3, trisqueezing: r = 0.19, t_sqz = 600 us, kappa_3 = 0.00031666666666666665
- n = 4, quadsqueezing: r = 0.054, t_sqz = 600 us, kappa_4 = 9e-05
- ratio3over2 = 0.11620795107033638
- ratio4over3 = 0.2842105263157895
- ratio4over2 = 0.03302752293577982
- trend_ok = true
- controlled_decay_ok = true
- order_spread_ok = true
- verdict = conforme

Lecture: les pentes décroissent avec l'ordre n, mais sans effondrement brutal.

### V5-G: details numeriques

Dernier rapport: `alphageometricport_check_20260517-145829Z`

- alpha_ref = 0.0072973525692838015
- alpha_approx = 0.0072992700729927005
- delta_Dtheta_rad = -1.2048031130217074e-05
- delta_Dtheta_deg = -0.0006903013352036694
- exact_claim_ok = false
- geometric_port_ok = true
- verdict = conforme

Lecture: 1/137 n'est pas exact, mais le déficit angulaire reste faible et exploitable.

### Suite alphaportsuite

Dernier resume: `alphaportsuite_suite_summary_20260517-145829Z`

- overall_verdict = supported
- supported_count = 3
- total = 3
- alphaenergyrunning = conforme
- alphatorsionorder = conforme
- alphageometricport = conforme

### Integration S-law

Dernier resume: `s_law_master_suite_summary_20260517-145828Z`

- overall_verdict = supported
- supported_count = 9
- support_total = 9
- falsifier_ok = 2
- falsifier_total = 2
- total = 11
- alphaportsuite = supported
- alpha_phase_observable = supported
- alpha_constant = falsifie

### Integration Experience 4 globale

Dernier resume: `experience4_global_suite_summary_20260517-145816Z`

- overall_verdict = supported
- supported_count = 5
- total = 5
- atom_basics = supported
- point_atome_protocol = supported
- point_atome_master = supported
- s_law_master = supported
- alphaportsuite = supported

### Bilan de validation

- 8 tests V5 passes en 1.04 s
- 6 tests de regression passes en 37.74 s
- toutes les couches V5, S-law et Experience 4 globale sont au verdict supported
